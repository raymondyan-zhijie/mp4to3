"""Main application window. All UI, zero business logic."""

from __future__ import annotations

import logging
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.models import (
    AppPaths,
    ConversionConfig,
    ConversionStatus,
    ConversionTask,
    HistoryRecord,
)
from core.config import ConfigManager
from core.history import HistoryStore
from core.engine import FFMpegConverter, SUPPORTED_EXTENSIONS, resolve_output_path
from ui.widgets import ScrollableFrame, DnDListbox

try:
    import winsound  # type: ignore
except ImportError:
    winsound = None


class MP4ToMP3ConverterApp:
    """Elderly-friendly video-to-audio converter application."""

    BITRATES = [
        "128k - 普通质量",
        "192k - 高质量 ★推荐",
        "256k - 极高质量",
        "320k - 最高质量",
    ]
    BITRATE_VALUES = ["128k", "192k", "256k", "320k"]

    def __init__(self, root: ttk.Window) -> None:
        self.root = root

        # --- Core services ---
        self._paths = AppPaths.create()
        self._setup_logging()
        self._config_mgr = ConfigManager(self._paths)
        self._config = self._config_mgr.load()
        self._history_store = HistoryStore(self._paths)
        self._engine = FFMpegConverter()

        # --- Runtime state ---
        self._files: list[str] = []
        self._converting = False
        self._last_tasks: list[ConversionTask] = []

        # --- Window setup ---
        self.root.title("MP4 转 MP3 转换器")
        self.root.state("zoomed")
        self.root.minsize(800, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # --- Build UI ---
        self._setup_drag_drop()       # must be before _create_widgets: DnDListbox needs tkdnd
        self._create_widgets()
        self._apply_config_to_ui()

        logging.info("应用程序启动")

    # ------------------------------------------------------------------
    # Init helpers
    # ------------------------------------------------------------------

    def _setup_logging(self) -> None:
        logging.basicConfig(
            filename=str(self._paths.log_file),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8",
        )

    def _apply_config_to_ui(self) -> None:
        try:
            idx = self.BITRATE_VALUES.index(self._config.bitrate)
            self._bitrate_var.set(self.BITRATES[idx])
        except ValueError:
            self._bitrate_var.set(self.BITRATES[1])
        self._output_path_var.set(self._config.output_dir)

    def _setup_drag_drop(self) -> None:
        import tkinterdnd2

        tkinterdnd2.TkinterDnD._require(self.root)
        self.root.drop_target_register("*")
        self.root.dnd_bind("<<Drop>>", self._on_root_drop)

    def _on_root_drop(self, event: tk.Event) -> None:
        if not event.data:
            return
        try:
            files = self.root.tk.splitlist(event.data)
        except Exception:
            files = event.data.split()
        cleaned = [f.strip("{}") for f in files if f.strip("{}")]
        if cleaned:
            self._handle_dropped_files(cleaned)

    # ------------------------------------------------------------------
    # Widget creation
    # ------------------------------------------------------------------

    def _create_widgets(self) -> None:
        """Build the full UI hierarchy."""
        container_outer = ttk.Frame(self.root)
        container_outer.pack(fill=BOTH, expand=YES)

        sf = ScrollableFrame(container_outer, padding=20)
        sf.pack(fill=BOTH, expand=YES)
        self._scrollable = sf

        main = sf.inner

        # --- Title ---
        title_frame = ttk.Frame(main)
        title_frame.pack(fill=X, pady=(0, 15))

        ttk.Label(
            title_frame,
            text="🎵 视频转音频工具",
            font=("微软雅黑", 24, "bold"),
            bootstyle="inverse-primary",
        ).pack()

        ttk.Label(
            title_frame,
            text="简单三步：选择视频 → 点击转换 → 完成",
            font=("微软雅黑", 13),
            bootstyle="secondary",
        ).pack(pady=(3, 0))

        # --- Step 1: File selection ---
        step1 = ttk.Labelframe(
            main,
            text="  第一步：选择要转换的视频文件  ",
            padding=15,
            bootstyle="primary",
        )
        step1.pack(fill=BOTH, expand=YES, pady=(0, 12))

        btn_container = ttk.Frame(step1)
        btn_container.pack(fill=X, pady=(0, 12))

        self._select_btn = ttk.Button(
            btn_container,
            text="📁 选择视频文件",
            command=self._on_select_files,
            bootstyle="success",
            width=20,
        )
        self._select_btn.pack(side=LEFT, padx=(0, 10))
        self._select_btn.configure(padding=12)

        self._clear_btn = ttk.Button(
            btn_container,
            text="🗑️ 清空列表",
            command=self._on_clear_files,
            bootstyle="secondary-outline",
            width=15,
        )
        self._clear_btn.pack(side=LEFT)
        self._clear_btn.configure(padding=12)

        self._file_count_var = tk.StringVar(value="尚未选择文件")
        ttk.Label(
            btn_container,
            textvariable=self._file_count_var,
            font=("微软雅黑", 16, "bold"),
            bootstyle="info",
        ).pack(side=LEFT, padx=(20, 0))

        list_container = ttk.Frame(step1)
        list_container.pack(fill=BOTH, expand=YES)

        list_scrollbar = ttk.Scrollbar(list_container)
        list_scrollbar.pack(side=RIGHT, fill=Y)

        self._file_listbox = DnDListbox(
            list_container,
            on_files_dropped=self._handle_dropped_files,
            font=("微软雅黑", 14),
            yscrollcommand=list_scrollbar.set,
            height=6,
            selectmode=tk.SINGLE,
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=1,
        )
        self._file_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        list_scrollbar.config(command=self._file_listbox.yview)

        # --- Step 2: Settings ---
        step2 = ttk.Labelframe(
            main,
            text="  第二步：设置转换选项（可选）  ",
            padding=15,
            bootstyle="info",
        )
        step2.pack(fill=X, pady=(0, 12))

        quality_container = ttk.Frame(step2)
        quality_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            quality_container,
            text="音质选择：",
            font=("微软雅黑", 16, "bold"),
        ).pack(side=LEFT, padx=(0, 10))

        self._bitrate_var = tk.StringVar(value=self.BITRATES[1])
        combo = ttk.Combobox(
            quality_container,
            textvariable=self._bitrate_var,
            values=self.BITRATES,
            state="readonly",
            font=("微软雅黑", 14),
            width=25,
        )
        combo.pack(side=LEFT)
        combo.bind("<<ComboboxSelected>>", self._on_settings_changed)

        output_container = ttk.Frame(step2)
        output_container.pack(fill=X)

        ttk.Label(
            output_container,
            text="保存位置：",
            font=("微软雅黑", 16, "bold"),
        ).pack(side=LEFT, padx=(0, 10))

        self._output_path_var = tk.StringVar()
        ttk.Entry(
            output_container,
            textvariable=self._output_path_var,
            state="readonly",
            font=("微软雅黑", 12),
            width=35,
        ).pack(side=LEFT, padx=(0, 10))

        browse_btn = ttk.Button(
            output_container,
            text="📂 更改位置",
            command=self._on_select_output_dir,
            bootstyle="info-outline",
            width=12,
        )
        browse_btn.pack(side=LEFT)
        browse_btn.configure(padding=8)

        # --- Step 3: Conversion ---
        step3 = ttk.Labelframe(
            main,
            text="  第三步：开始转换  ",
            padding=15,
            bootstyle="success",
        )
        step3.pack(fill=X, pady=(0, 12))

        self._progress_var = tk.DoubleVar()
        self._progress_bar = ttk.Progressbar(
            step3,
            variable=self._progress_var,
            maximum=100,
            bootstyle="success-striped",
            length=400,
        )
        self._progress_bar.pack(fill=X, pady=(0, 15))

        self._status_var = tk.StringVar(value="准备就绪，请选择视频文件")
        ttk.Label(
            step3,
            textvariable=self._status_var,
            font=("微软雅黑", 14),
            bootstyle="secondary",
            anchor=CENTER,
        ).pack(fill=X, pady=(0, 15))

        action_container = ttk.Frame(step3)
        action_container.pack()

        self._start_btn = ttk.Button(
            action_container,
            text="🚀 开始转换",
            command=self._on_start_conversion,
            bootstyle="success",
            width=25,
        )
        self._start_btn.pack(side=LEFT, padx=(0, 15))
        self._start_btn.configure(padding=15)

        self._cancel_btn = ttk.Button(
            action_container,
            text="⏹️ 取消转换",
            command=self._on_cancel_conversion,
            bootstyle="danger",
            state=DISABLED,
            width=20,
        )
        self._cancel_btn.pack(side=LEFT)
        self._cancel_btn.configure(padding=15)

        # --- History button ---
        history_btn = ttk.Button(
            main,
            text="📋 查看转换历史",
            command=self._on_show_history,
            bootstyle="secondary-outline",
            width=20,
        )
        history_btn.pack(pady=(10, 0))
        history_btn.configure(padding=10)

    # ------------------------------------------------------------------
    # Event handlers — file selection
    # ------------------------------------------------------------------

    def _on_select_files(self) -> None:
        files = filedialog.askopenfilenames(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4;*.avi;*.mkv;*.mov;*.flv;*.wmv;*.m4v"),
                ("所有文件", "*.*"),
            ],
        )
        if files:
            self._handle_dropped_files(list(files))

    def _on_clear_files(self) -> None:
        self._files.clear()
        self._update_file_list()
        logging.info("文件列表已清空")

    def _handle_dropped_files(self, file_paths: list[str]) -> None:
        skipped = 0
        for path_str in file_paths:
            if path_str in self._files:
                skipped += 1
                continue
            ext = os.path.splitext(path_str)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                logging.warning(f"不支持的文件格式，已跳过: {os.path.basename(path_str)}")
                skipped += 1
                continue
            self._files.append(path_str)
        self._update_file_list()
        if skipped:
            messagebox.showwarning("提示", f"已跳过 {skipped} 个不支持或不重复的文件")
        logging.info(f"处理了 {len(file_paths)} 个文件，有效 {len(file_paths) - skipped} 个")

    def _update_file_list(self) -> None:
        self._file_listbox.delete(0, tk.END)
        for f in self._files:
            self._file_listbox.insert(tk.END, f"  ▸ {os.path.basename(f)}")
        if self._files:
            self._file_count_var.set(f"已选择 {len(self._files)} 个文件")
            self._status_var.set("文件已选择，点击【开始转换】按钮")
        else:
            self._file_count_var.set("尚未选择文件")
            self._status_var.set("准备就绪，请选择视频文件")

    # ------------------------------------------------------------------
    # Event handlers — settings
    # ------------------------------------------------------------------

    def _on_select_output_dir(self) -> None:
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self._output_path_var.get(),
        )
        if not directory:
            return
        if not os.path.exists(directory):
            messagebox.showerror("错误", "所选目录不存在！")
            return
        if not os.access(directory, os.W_OK):
            messagebox.showerror("错误", "所选目录没有写入权限！")
            return
        self._output_path_var.set(directory)
        self._config.output_dir = directory
        self._config_mgr.save(self._config)

    def _on_settings_changed(self, event: tk.Event | None = None) -> None:
        selected = self._bitrate_var.get()
        try:
            idx = self.BITRATES.index(selected)
            self._config.bitrate = self.BITRATE_VALUES[idx]
            self._config_mgr.save(self._config)
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Event handlers — conversion
    # ------------------------------------------------------------------

    def _on_start_conversion(self) -> None:
        if not self._files:
            messagebox.showwarning(
                "提示",
                "请先选择视频文件！\n\n点击【选择视频文件】按钮来选择要转换的文件。",
            )
            return
        output_dir = self._output_path_var.get()
        if not os.path.exists(output_dir):
            messagebox.showerror("错误", "输出目录不存在！")
            return
        if self._converting:
            return

        self._converting = True
        self._start_btn.config(state=DISABLED)
        self._cancel_btn.config(state=NORMAL)
        self._select_btn.config(state=DISABLED)
        self._clear_btn.config(state=DISABLED)

        bitrate = self._get_selected_bitrate()
        output_path = Path(output_dir)
        tasks = [
            ConversionTask(
                source_path=Path(f),
                output_path=resolve_output_path(output_path, os.path.basename(f)),
                bitrate=bitrate,
                sample_rate=self._config.sample_rate,
            )
            for f in self._files
        ]

        self._last_tasks = tasks
        self._engine.reset_cancel()
        logging.info(f"开始转换 {len(tasks)} 个文件")

        t = threading.Thread(target=self._run_conversion, args=(tasks,), daemon=True)
        t.start()

    def _on_cancel_conversion(self) -> None:
        if messagebox.askyesno("确认", "确定要取消转换吗？"):
            self._engine.cancel()
            self._status_var.set("正在取消转换...")
            logging.info("用户请求取消转换")

    def _get_selected_bitrate(self) -> str:
        selected = self._bitrate_var.get()
        try:
            return self.BITRATE_VALUES[self.BITRATES.index(selected)]
        except ValueError:
            return "192k"

    # ------------------------------------------------------------------
    # Conversion thread
    # ------------------------------------------------------------------

    def _run_conversion(self, tasks: list[ConversionTask]) -> None:
        try:
            self._engine.convert_batch(
                tasks,
                on_progress=self._on_convert_progress,
                on_task_done=self._on_convert_task_done,
            )
        finally:
            self.root.after(0, self._on_conversion_finished)

    def _on_convert_progress(self, done: int, total: int, filename: str) -> None:
        self.root.after(
            0,
            lambda: self._status_var.set(
                f"⏳ 正在转换：{filename} ({done}/{total})"
            ),
        )
        self.root.after(0, lambda: self._progress_var.set((done / total) * 100))

    def _on_convert_task_done(self, task: ConversionTask) -> None:
        if task.status == ConversionStatus.COMPLETED:
            record = HistoryRecord(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                source_name=task.source_path.name,
                output_name=task.output_path.name,
                source_path=str(task.source_path),
                output_path=str(task.output_path),
                bitrate=task.bitrate,
                duration=task.duration or 0.0,
                status="completed",
            )
            self.root.after(0, lambda r=record: self._history_store.add(r))
            logging.info(
                f"转换成功: {task.source_path.name} -> {task.output_path.name}"
            )
        elif task.status == ConversionStatus.FAILED:
            self.root.after(
                0,
                lambda t=task: messagebox.showerror(
                    "转换错误",
                    f"转换 {t.source_path.name} 时出错:\n\n{t.error_message}",
                ),
            )

    # ------------------------------------------------------------------
    # Conversion finished (UI thread)
    # ------------------------------------------------------------------

    def _on_conversion_finished(self) -> None:
        self._converting = False
        self._start_btn.config(state=NORMAL)
        self._cancel_btn.config(state=DISABLED)
        self._select_btn.config(state=NORMAL)
        self._clear_btn.config(state=NORMAL)

        if not self._last_tasks:
            return

        successful = sum(
            1 for t in self._last_tasks if t.status == ConversionStatus.COMPLETED
        )
        failed = sum(
            1 for t in self._last_tasks if t.status == ConversionStatus.FAILED
        )
        cancelled = any(
            t.status == ConversionStatus.CANCELLED for t in self._last_tasks
        )

        if cancelled and successful == 0 and failed == 0:
            self._status_var.set("❌ 转换已取消")
            logging.info("转换已取消")
        else:
            total_time = sum(t.duration or 0 for t in self._last_tasks)
            self._status_var.set(
                f"✅ 转换完成！成功 {successful} 个，失败 {failed} 个，"
                f"耗时 {timedelta(seconds=int(total_time))}"
            )
            self._progress_var.set(100)

            if winsound:
                try:
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                except Exception:
                    pass

            messagebox.showinfo(
                "转换完成",
                f"🎉 转换完成！\n\n"
                f"✅ 成功：{successful} 个\n"
                f"❌ 失败：{failed} 个\n"
                f"⏱️ 总耗时：{timedelta(seconds=int(total_time))}\n\n"
                f"文件已保存到：\n{self._output_path_var.get()}",
            )
            logging.info(f"转换完成: 成功 {successful}, 失败 {failed}")

    # ------------------------------------------------------------------
    # History window
    # ------------------------------------------------------------------

    def _on_show_history(self) -> None:
        self._show_history_window()

    def _show_history_window(self) -> None:
        win = ttk.Toplevel(self.root)
        win.title("转换历史记录")
        win.geometry("900x600")

        container = ttk.Frame(win, padding=20)
        container.pack(fill=BOTH, expand=YES)

        ttk.Label(
            container,
            text="📋 转换历史记录",
            font=("微软雅黑", 20, "bold"),
            bootstyle="primary",
        ).pack(pady=(0, 20))

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, pady=(0, 10))

        clear_btn = ttk.Button(
            btn_frame,
            text="🗑️ 清空历史",
            command=lambda: self._clear_history_with_refresh(win),
            bootstyle="danger-outline",
        )
        clear_btn.pack(side=RIGHT)
        clear_btn.configure(padding=10)

        records = self._history_store.get_all()
        if records:
            text_frame = ttk.Frame(container)
            text_frame.pack(fill=BOTH, expand=YES)

            sb = ttk.Scrollbar(text_frame)
            sb.pack(side=RIGHT, fill=Y)

            text_widget = tk.Text(
                text_frame,
                font=("微软雅黑", 12),
                yscrollcommand=sb.set,
                wrap=tk.WORD,
                relief=tk.FLAT,
                borderwidth=2,
            )
            text_widget.pack(side=LEFT, fill=BOTH, expand=YES)
            sb.config(command=text_widget.yview)

            for i, item in enumerate(reversed(records), 1):
                text_widget.insert(tk.END, f"【记录 {i}】\n", "title")
                text_widget.insert(tk.END, f"时间：{item.timestamp}\n")
                text_widget.insert(tk.END, f"源文件：{item.source_name}\n")
                text_widget.insert(tk.END, f"输出：{item.output_name}\n")
                text_widget.insert(tk.END, f"音质：{item.bitrate}  耗时：{item.duration:.0f}秒\n")
                text_widget.insert(tk.END, "\n" + "-" * 80 + "\n\n")

            text_widget.tag_config(
                "title", font=("微软雅黑", 13, "bold"), foreground="#0d6efd"
            )
            text_widget.config(state=tk.DISABLED)
        else:
            ttk.Label(
                container,
                text="暂无转换记录",
                font=("微软雅黑", 16),
                bootstyle="secondary",
            ).pack(expand=YES)

    def _clear_history_with_refresh(self, window: tk.Toplevel) -> None:
        if messagebox.askyesno("确认", "确定要清空所有转换历史记录吗？", parent=window):
            self._history_store.clear()
            window.destroy()
            self._show_history_window()

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def _on_closing(self) -> None:
        if self._converting:
            if messagebox.askokcancel("退出", "转换正在进行中，确定要退出吗？"):
                self._engine.cancel()
                self._history_store.close()
                logging.info("应用程序关闭")
                self.root.destroy()
        else:
            self._history_store.close()
            logging.info("应用程序关闭")
            self.root.destroy()
