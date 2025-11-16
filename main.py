"""
MP4 to MP3 Converter - 老年人友好版
一个界面简洁、字体超大、易于操作的视频到音频转换工具
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from moviepy import VideoFileClip
import time
from datetime import datetime, timedelta
import winsound
import threading
import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    filename='converter.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class MP4ToMP3Converter:
    """MP4 到 MP3 转换器 - 老年人友好版"""

    def __init__(self, root):
        """初始化转换器应用"""
        self.root = root
        self.root.title("MP4 转 MP3 转换器")

        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 默认最大化窗口（适合老年人）
        self.root.state('zoomed')  # Windows 上最大化

        # 设置最小窗口大小
        self.root.minsize(800, 600)
        self.root.resizable(True, True)

        # 存储屏幕尺寸用于响应式调整
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 应用数据目录
        self.app_data_dir = Path(os.getenv('APPDATA')) / 'MP4to3'
        self.app_data_dir.mkdir(exist_ok=True)

        # 文件列表
        self.files = []

        # 转换参数
        self.bitrates = ["128k - 普通质量", "192k - 高质量 ★推荐", "256k - 极高质量", "320k - 最高质量"]
        self.bitrate_values = ["128k", "192k", "256k", "320k"]

        # 转换状态
        self.converting = False
        self.cancel_event = threading.Event()

        # 配置文件
        self.config_file = self.app_data_dir / 'config.json'
        self.load_config()

        # 历史记录文件
        self.history_file = self.app_data_dir / 'conversion_history.json'
        self.load_history()

        # 创建界面
        self.create_widgets()

        # 应用保存的配置
        self.apply_config()

        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        logging.info("应用程序启动")

    def load_config(self):
        """加载用户配置"""
        self.config = {
            'bitrate': '192k',
            'output_dir': os.path.expanduser("~\\Music")
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                logging.info("配置加载成功")
            except Exception as e:
                logging.error(f"加载配置失败: {e}")

    def save_config(self):
        """保存用户配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logging.info("配置保存成功")
        except Exception as e:
            logging.error(f"保存配置失败: {e}")

    def apply_config(self):
        """应用保存的配置到界面"""
        # 设置比特率
        bitrate = self.config.get('bitrate', '192k')
        try:
            index = self.bitrate_values.index(bitrate)
            self.bitrate_var.set(self.bitrates[index])
        except:
            self.bitrate_var.set(self.bitrates[1])  # 默认192k

        self.output_path.set(self.config.get('output_dir', os.path.expanduser("~\\Music")))

    def create_widgets(self):
        """创建所有界面组件"""
        # 创建可滚动的容器
        # 外层容器
        container_outer = ttk.Frame(self.root)
        container_outer.pack(fill=BOTH, expand=YES)

        # 创建 Canvas 和 Scrollbar
        canvas = tk.Canvas(container_outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_outer, orient=VERTICAL, command=canvas.yview)

        # 可滚动的主框架
        main_container = ttk.Frame(canvas, padding=20)

        # 配置滚动
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)

        # 将主容器添加到 canvas
        canvas_frame = canvas.create_window((0, 0), window=main_container, anchor=NW)

        # 配置滚动区域
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 确保框架宽度填充canvas
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(canvas_frame, width=canvas_width)

        main_container.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)

        # 鼠标滚轮支持
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # 存储 canvas 引用用于后续操作
        self.canvas = canvas
        self.main_container = main_container

        # ==================== 标题区域 ====================
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=X, pady=(0, 15))

        title_label = ttk.Label(
            title_frame,
            text="🎵 视频转音频工具",
            font=("微软雅黑", 24, "bold"),
            bootstyle="inverse-primary"
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="简单三步：选择视频 → 点击转换 → 完成",
            font=("微软雅黑", 13),
            bootstyle="secondary"
        )
        subtitle_label.pack(pady=(3, 0))

        # ==================== 步骤1: 选择文件 ====================
        step1_frame = ttk.Labelframe(
            main_container,
            text="  第一步：选择要转换的视频文件  ",
            padding=15,
            bootstyle="primary"
        )
        step1_frame.pack(fill=BOTH, expand=YES, pady=(0, 12))

        # 按钮容器
        button_container = ttk.Frame(step1_frame)
        button_container.pack(fill=X, pady=(0, 12))

        # 选择文件按钮（大号）
        self.select_btn = ttk.Button(
            button_container,
            text="📁 选择视频文件",
            command=self.select_files,
            bootstyle="success",
            width=20
        )
        self.select_btn.pack(side=LEFT, padx=(0, 10))
        self.select_btn.configure(padding=12)

        # 清空按钮
        self.clear_btn = ttk.Button(
            button_container,
            text="🗑️ 清空列表",
            command=self.clear_files,
            bootstyle="secondary-outline",
            width=15
        )
        self.clear_btn.pack(side=LEFT)
        self.clear_btn.configure(padding=12)

        # 文件数量显示
        self.file_count_var = tk.StringVar(value="尚未选择文件")
        count_label = ttk.Label(
            button_container,
            textvariable=self.file_count_var,
            font=("微软雅黑", 16, "bold"),
            bootstyle="info"
        )
        count_label.pack(side=LEFT, padx=(20, 0))

        # 文件列表（使用更大的字体）
        list_container = ttk.Frame(step1_frame)
        list_container.pack(fill=BOTH, expand=YES)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.file_listbox = tk.Listbox(
            list_container,
            font=("微软雅黑", 14),
            yscrollcommand=scrollbar.set,
            height=6,
            selectmode=tk.SINGLE,
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=1
        )
        self.file_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.config(command=self.file_listbox.yview)

        # ==================== 步骤2: 设置选项 ====================
        step2_frame = ttk.Labelframe(
            main_container,
            text="  第二步：设置转换选项（可选）  ",
            padding=15,
            bootstyle="info"
        )
        step2_frame.pack(fill=X, pady=(0, 12))

        # 音质选择
        quality_container = ttk.Frame(step2_frame)
        quality_container.pack(fill=X, pady=(0, 10))

        quality_label = ttk.Label(
            quality_container,
            text="音质选择：",
            font=("微软雅黑", 16, "bold")
        )
        quality_label.pack(side=LEFT, padx=(0, 10))

        self.bitrate_var = tk.StringVar(value="192k - 高质量 ★推荐")
        bitrate_combo = ttk.Combobox(
            quality_container,
            textvariable=self.bitrate_var,
            values=self.bitrates,
            state="readonly",
            font=("微软雅黑", 14),
            width=25
        )
        bitrate_combo.pack(side=LEFT)
        bitrate_combo.bind('<<ComboboxSelected>>', self.on_settings_changed)

        # 输出目录
        output_container = ttk.Frame(step2_frame)
        output_container.pack(fill=X)

        output_label = ttk.Label(
            output_container,
            text="保存位置：",
            font=("微软雅黑", 16, "bold")
        )
        output_label.pack(side=LEFT, padx=(0, 10))

        self.output_path = tk.StringVar(value=os.path.expanduser("~\\Music"))
        output_entry = ttk.Entry(
            output_container,
            textvariable=self.output_path,
            state="readonly",
            font=("微软雅黑", 12),
            width=35
        )
        output_entry.pack(side=LEFT, padx=(0, 10))

        browse_btn = ttk.Button(
            output_container,
            text="📂 更改位置",
            command=self.select_output_dir,
            bootstyle="info-outline",
            width=12
        )
        browse_btn.pack(side=LEFT)
        browse_btn.configure(padding=8)

        # ==================== 步骤3: 开始转换 ====================
        step3_frame = ttk.Labelframe(
            main_container,
            text="  第三步：开始转换  ",
            padding=15,
            bootstyle="success"
        )
        step3_frame.pack(fill=X, pady=(0, 12))

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            step3_frame,
            variable=self.progress_var,
            maximum=100,
            bootstyle="success-striped",
            length=400
        )
        self.progress_bar.pack(fill=X, pady=(0, 15))

        # 状态显示
        self.status_var = tk.StringVar(value="准备就绪，请选择视频文件")
        status_label = ttk.Label(
            step3_frame,
            textvariable=self.status_var,
            font=("微软雅黑", 14),
            bootstyle="secondary",
            anchor=CENTER
        )
        status_label.pack(fill=X, pady=(0, 15))

        # 转换按钮（大号、醒目）
        button_container = ttk.Frame(step3_frame)
        button_container.pack()

        self.start_button = ttk.Button(
            button_container,
            text="🚀 开始转换",
            command=self.start_conversion,
            bootstyle="success",
            width=25
        )
        self.start_button.pack(side=LEFT, padx=(0, 15))
        self.start_button.configure(padding=15)

        self.cancel_button = ttk.Button(
            button_container,
            text="⏹️ 取消转换",
            command=self.cancel_conversion,
            bootstyle="danger",
            state=DISABLED,
            width=20
        )
        self.cancel_button.pack(side=LEFT)
        self.cancel_button.configure(padding=15)

        # ==================== 历史记录按钮 ====================
        history_btn = ttk.Button(
            main_container,
            text="📋 查看转换历史",
            command=self.show_history,
            bootstyle="secondary-outline",
            width=20
        )
        history_btn.pack(pady=(10, 0))
        history_btn.configure(padding=10)

    def load_history(self):
        """加载转换历史记录"""
        self.conversion_history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.conversion_history = json.load(f)
                logging.info(f"历史记录加载成功，共 {len(self.conversion_history)} 条记录")
            except Exception as e:
                logging.error(f"加载历史记录失败: {e}")

    def save_history(self):
        """保存转换历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversion_history, f, ensure_ascii=False, indent=2)
            logging.info("历史记录保存成功")
        except Exception as e:
            logging.error(f"保存历史记录失败: {e}")

    def add_to_history(self, source_file, output_file, bitrate, duration):
        """添加记录到转换历史"""
        history_item = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': source_file,
            'output': output_file,
            'bitrate': bitrate,
            'duration': str(duration)
        }
        self.conversion_history.append(history_item)
        self.save_history()

    def show_history(self):
        """显示历史记录窗口"""
        history_window = ttk.Toplevel(self.root)
        history_window.title("转换历史记录")
        history_window.geometry("900x600")

        # 主容器
        container = ttk.Frame(history_window, padding=20)
        container.pack(fill=BOTH, expand=YES)

        # 标题
        title = ttk.Label(
            container,
            text="📋 转换历史记录",
            font=("微软雅黑", 20, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=(0, 20))

        # 按钮框
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, pady=(0, 10))

        clear_btn = ttk.Button(
            btn_frame,
            text="🗑️ 清空历史",
            command=lambda: self.clear_history_with_refresh(history_window),
            bootstyle="danger-outline"
        )
        clear_btn.pack(side=RIGHT)
        clear_btn.configure(padding=10)

        # 历史列表
        if self.conversion_history:
            # 使用文本框显示历史（更易读）
            text_frame = ttk.Frame(container)
            text_frame.pack(fill=BOTH, expand=YES)

            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side=RIGHT, fill=Y)

            history_text = tk.Text(
                text_frame,
                font=("微软雅黑", 12),
                yscrollcommand=scrollbar.set,
                wrap=tk.WORD,
                relief=tk.FLAT,
                borderwidth=2
            )
            history_text.pack(side=LEFT, fill=BOTH, expand=YES)
            scrollbar.config(command=history_text.yview)

            # 填充历史记录
            for i, item in enumerate(reversed(self.conversion_history), 1):
                history_text.insert(END, f"【记录 {i}】\n", "title")
                history_text.insert(END, f"时间：{item['time']}\n")
                history_text.insert(END, f"源文件：{os.path.basename(item['source'])}\n")
                history_text.insert(END, f"输出：{os.path.basename(item['output'])}\n")
                history_text.insert(END, f"音质：{item['bitrate']}  耗时：{item['duration']}\n")
                history_text.insert(END, "\n" + "-"*80 + "\n\n")

            history_text.tag_config("title", font=("微软雅黑", 13, "bold"), foreground="#0d6efd")
            history_text.config(state=DISABLED)
        else:
            no_history = ttk.Label(
                container,
                text="暂无转换记录",
                font=("微软雅黑", 16),
                bootstyle="secondary"
            )
            no_history.pack(expand=YES)

    def clear_history_with_refresh(self, window):
        """清空历史记录并刷新窗口"""
        if messagebox.askyesno('确认', '确定要清空所有转换历史记录吗？', parent=window):
            self.conversion_history = []
            self.save_history()
            logging.info("历史记录已清空")
            window.destroy()
            self.show_history()

    def select_files(self):
        """选择要转换的文件"""
        files = filedialog.askopenfilenames(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4;*.avi;*.mkv;*.mov;*.flv;*.wmv;*.m4v"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            # 避免重复添加
            for file in files:
                if file not in self.files:
                    self.files.append(file)
            self.update_file_list()
            logging.info(f"选择了 {len(files)} 个文件")

    def clear_files(self):
        """清空文件选择"""
        self.files.clear()
        self.update_file_list()
        logging.info("文件列表已清空")

    def update_file_list(self):
        """更新文件列表显示"""
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            self.file_listbox.insert(tk.END, f"  ▸ {os.path.basename(file)}")

        if len(self.files) > 0:
            self.file_count_var.set(f"已选择 {len(self.files)} 个文件")
            self.status_var.set("文件已选择，点击【开始转换】按钮")
        else:
            self.file_count_var.set("尚未选择文件")
            self.status_var.set("准备就绪，请选择视频文件")

    def select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.output_path.get()
        )
        if directory:
            # 验证目录是否存在
            if not os.path.exists(directory):
                messagebox.showerror("错误", "所选目录不存在！")
                logging.error(f"选择的目录不存在: {directory}")
                return

            # 验证是否有写入权限
            if not os.access(directory, os.W_OK):
                messagebox.showerror("错误", "所选目录没有写入权限！")
                logging.error(f"目录无写入权限: {directory}")
                return

            self.output_path.set(directory)
            self.config['output_dir'] = directory
            self.save_config()
            logging.info(f"输出目录已设置为: {directory}")

    def on_settings_changed(self, event=None):
        """当设置改变时保存配置"""
        # 获取实际的比特率值
        selected = self.bitrate_var.get()
        try:
            index = self.bitrates.index(selected)
            self.config['bitrate'] = self.bitrate_values[index]
            self.save_config()
        except:
            pass

    def start_conversion(self):
        """开始转换"""
        if not self.files:
            messagebox.showwarning("提示", "请先选择视频文件！\n\n点击【选择视频文件】按钮来选择要转换的文件。")
            return

        # 验证输出目录
        output_dir = self.output_path.get()
        if not os.path.exists(output_dir):
            messagebox.showerror("错误", "输出目录不存在！")
            return

        if self.converting:
            return

        # 重置取消标志
        self.cancel_event.clear()

        self.converting = True
        self.start_button.config(state=DISABLED)
        self.cancel_button.config(state=NORMAL)
        self.select_btn.config(state=DISABLED)
        self.clear_btn.config(state=DISABLED)

        logging.info(f"开始转换 {len(self.files)} 个文件")

        # 启动转换线程
        conversion_thread = threading.Thread(target=self.convert_files, daemon=True)
        conversion_thread.start()

    def cancel_conversion(self):
        """取消转换"""
        if messagebox.askyesno("确认", "确定要取消转换吗？"):
            self.cancel_event.set()
            self.root.after(0, lambda: self.status_var.set("正在取消转换..."))
            logging.info("用户请求取消转换")

    def convert_files(self):
        """转换文件（在单独的线程中运行）"""
        total_start_time = time.time()
        total_files = len(self.files)
        successful = 0
        failed = 0

        # 获取实际的比特率值
        selected = self.bitrate_var.get()
        try:
            index = self.bitrates.index(selected)
            bitrate = self.bitrate_values[index]
        except:
            bitrate = "192k"

        for index, file in enumerate(self.files):
            # 检查是否取消
            if self.cancel_event.is_set():
                self.root.after(0, lambda: self.status_var.set("❌ 转换已取消"))
                logging.info("转换已取消")
                break

            try:
                file_start_time = time.time()
                file_name = os.path.basename(file)

                # 更新状态（线程安全）
                self.root.after(0, lambda fn=file_name, i=index, t=total_files:
                              self.status_var.set(f"⏳ 正在转换：{fn} ({i + 1}/{t})"))

                # 设置输出文件路径
                output_file = os.path.join(
                    self.output_path.get(),
                    os.path.splitext(file_name)[0] + ".mp3"
                )

                # 检查输出文件是否已存在
                if os.path.exists(output_file):
                    base_name = os.path.splitext(file_name)[0]
                    counter = 1
                    while os.path.exists(output_file):
                        output_file = os.path.join(
                            self.output_path.get(),
                            f"{base_name}_{counter}.mp3"
                        )
                        counter += 1

                logging.info(f"正在转换: {file_name}")

                # 转换文件
                video = VideoFileClip(file)
                audio = video.audio

                if audio is None:
                    raise Exception("视频文件没有音频轨道")

                # 设置音频参数
                audio.write_audiofile(
                    output_file,
                    bitrate=bitrate,
                    fps=44100,
                    logger=None
                )

                # 关闭资源
                audio.close()
                video.close()

                # 更新进度（线程安全）
                progress = ((index + 1) / total_files) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))

                # 添加到历史记录
                file_duration = time.time() - file_start_time
                self.add_to_history(
                    file,
                    output_file,
                    bitrate,
                    timedelta(seconds=int(file_duration))
                )

                successful += 1
                logging.info(f"转换成功: {file_name} -> {os.path.basename(output_file)}")

            except Exception as e:
                failed += 1
                error_msg = f"转换 {file_name} 时出错:\n\n{str(e)}"
                logging.error(error_msg)
                self.root.after(0, lambda msg=error_msg:
                              messagebox.showerror("转换错误", msg))

        # 转换完成处理
        if not self.cancel_event.is_set():
            total_time = time.time() - total_start_time
            status_msg = f"✅ 转换完成！成功 {successful} 个，失败 {failed} 个，耗时 {timedelta(seconds=int(total_time))}"
            self.root.after(0, lambda msg=status_msg: self.status_var.set(msg))
            self.root.after(0, lambda: self.progress_var.set(100))

            # 播放完成提示音
            try:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            except:
                pass

            # 显示完成消息
            completion_msg = f"🎉 转换完成！\n\n✅ 成功：{successful} 个\n❌ 失败：{failed} 个\n⏱️ 总耗时：{timedelta(seconds=int(total_time))}\n\n文件已保存到：\n{self.output_path.get()}"
            self.root.after(0, lambda msg=completion_msg:
                          messagebox.showinfo("转换完成", msg))

            logging.info(f"转换完成: 成功 {successful}, 失败 {failed}")

        # 重置状态
        self.converting = False
        self.root.after(0, lambda: self.start_button.config(state=NORMAL))
        self.root.after(0, lambda: self.cancel_button.config(state=DISABLED))
        self.root.after(0, lambda: self.select_btn.config(state=NORMAL))
        self.root.after(0, lambda: self.clear_btn.config(state=NORMAL))

    def on_closing(self):
        """窗口关闭事件处理"""
        if self.converting:
            if messagebox.askokcancel("退出", "转换正在进行中，确定要退出吗？"):
                self.cancel_event.set()
                logging.info("应用程序关闭")
                self.root.destroy()
        else:
            logging.info("应用程序关闭")
            self.root.destroy()

def main():
    """主函数"""
    # 使用现代主题
    root = ttk.Window(
        title="MP4 转 MP3 转换器",
        themename="cosmo",  # 现代、清新的主题
        size=(1000, 750)
    )

    # 设置全局字体
    style = ttk.Style()
    style.configure('.', font=('微软雅黑', 12))
    style.configure('TButton', font=('微软雅黑', 14, 'bold'))
    style.configure('TLabel', font=('微软雅黑', 12))
    style.configure('TLabelframe.Label', font=('微软雅黑', 16, 'bold'))

    app = MP4ToMP3Converter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
