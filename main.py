"""
MP4 to MP3 Converter
一个功能强大的视频到音频转换工具，支持批量处理、多种格式和详细的历史记录。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
    """MP4 到 MP3 转换器主类"""

    def __init__(self, root):
        """初始化转换器应用"""
        self.root = root
        self.root.title("MP4 转 MP3 转换器 v2.0")
        self.root.geometry("850x650")
        self.root.resizable(True, True)

        # 应用数据目录
        self.app_data_dir = Path(os.getenv('APPDATA')) / 'MP4to3'
        self.app_data_dir.mkdir(exist_ok=True)

        # 文件列表
        self.files = []

        # 转换参数
        self.bitrates = ["128k", "192k", "256k", "320k"]
        self.sample_rates = ["44100", "48000", "96000"]

        # 转换状态
        self.converting = False
        self.cancel_event = threading.Event()

        # 配置文件
        self.config_file = self.app_data_dir / 'config.json'
        self.load_config()

        # 历史记录文件
        self.history_file = self.app_data_dir / 'conversion_history.json'
        self.load_history()

        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # 主转换页面
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text='转换')

        # 历史记录页面
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text='历史记录')

        # 创建界面元素
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
            'sample_rate': '44100',
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
        self.bitrate_var.set(self.config.get('bitrate', '192k'))
        self.sample_rate_var.set(self.config.get('sample_rate', '44100'))
        self.output_path.set(self.config.get('output_dir', os.path.expanduser("~\\Music")))

    def create_widgets(self):
        """创建所有界面组件"""
        self.create_main_tab()
        self.create_history_tab()

    def create_main_tab(self):
        """创建主转换标签页"""
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.main_frame, text="文件选择", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(file_frame, text="选择文件", command=self.select_files).pack(side="left", padx=5)
        ttk.Button(file_frame, text="清空选择", command=self.clear_files).pack(side="left", padx=5)

        # 文件数量显示
        self.file_count_var = tk.StringVar(value="已选择: 0 个文件")
        ttk.Label(file_frame, textvariable=self.file_count_var).pack(side="left", padx=10)

        # 文件列表显示
        list_frame = ttk.LabelFrame(self.main_frame, text="已选文件列表", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # 转换选项区域
        options_frame = ttk.LabelFrame(self.main_frame, text="转换选项", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)

        # 比特率选择
        ttk.Label(options_frame, text="比特率:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.bitrate_var = tk.StringVar(value="192k")
        bitrate_combo = ttk.Combobox(options_frame, textvariable=self.bitrate_var,
                                     values=self.bitrates, state="readonly", width=10)
        bitrate_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        bitrate_combo.bind('<<ComboboxSelected>>', self.on_settings_changed)

        # 采样率选择
        ttk.Label(options_frame, text="采样率:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.sample_rate_var = tk.StringVar(value="44100")
        sample_rate_combo = ttk.Combobox(options_frame, textvariable=self.sample_rate_var,
                                        values=self.sample_rates, state="readonly", width=10)
        sample_rate_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        sample_rate_combo.bind('<<ComboboxSelected>>', self.on_settings_changed)

        # 输出目录选择
        output_frame = ttk.LabelFrame(self.main_frame, text="输出目录", padding=10)
        output_frame.pack(fill="x", padx=10, pady=5)

        self.output_path = tk.StringVar(value=os.path.expanduser("~\\Music"))
        ttk.Entry(output_frame, textvariable=self.output_path, state="readonly").pack(
            side="left", fill="x", expand=True, padx=5)
        ttk.Button(output_frame, text="浏览", command=self.select_output_dir).pack(side="left", padx=5)

        # 进度显示区域
        progress_frame = ttk.LabelFrame(self.main_frame, text="转换进度", padding=10)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=5, pady=5)

        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(pady=5)

        # 转换按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="开始转换",
                                       command=self.start_conversion)
        self.start_button.pack(side="left", padx=5)

        self.cancel_button = ttk.Button(button_frame, text="取消",
                                        command=self.cancel_conversion, state="disabled")
        self.cancel_button.pack(side="left", padx=5)

    def create_history_tab(self):
        """创建历史记录标签页"""
        # 搜索和控制框
        search_frame = ttk.Frame(self.history_frame)
        search_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(search_frame, text="搜索:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_history)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(
            side='left', fill='x', expand=True, padx=5)
        ttk.Button(search_frame, text='清空历史',
                  command=self.clear_history).pack(side='right', padx=5)

        # 历史记录列表
        columns = ('时间', '源文件', '输出文件', '比特率', '采样率', '耗时')
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show='headings')

        # 设置列标题和宽度
        column_widths = {
            '时间': 150,
            '源文件': 200,
            '输出文件': 200,
            '比特率': 80,
            '采样率': 100,
            '耗时': 100
        }

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=column_widths.get(col, 100))

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.history_frame, orient='vertical',
                                 command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        self.history_tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side='right', fill='y', padx=(0, 10), pady=5)

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

    def add_to_history(self, source_file, output_file, bitrate, sample_rate, duration):
        """添加记录到转换历史"""
        history_item = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': source_file,
            'output': output_file,
            'bitrate': bitrate,
            'sample_rate': sample_rate,
            'duration': str(duration)
        }
        self.conversion_history.append(history_item)
        self.save_history()

        # 使用线程安全的方式更新UI
        self.root.after(0, self.update_history_display)

    def update_history_display(self, filter_text=''):
        """更新历史记录显示"""
        self.history_tree.delete(*self.history_tree.get_children())
        for item in reversed(self.conversion_history):
            if (filter_text.lower() in item['source'].lower() or
                filter_text.lower() in item['output'].lower()):
                self.history_tree.insert('', 'end', values=(
                    item['time'],
                    os.path.basename(item['source']),
                    os.path.basename(item['output']),
                    item['bitrate'],
                    item['sample_rate'],
                    item['duration']
                ))

    def filter_history(self, *args):
        """过滤历史记录"""
        self.update_history_display(self.search_var.get())

    def clear_history(self):
        """清空历史记录"""
        if messagebox.askyesno('确认', '确定要清空所有转换历史记录吗？'):
            self.conversion_history = []
            self.save_history()
            self.update_history_display()
            logging.info("历史记录已清空")

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
            self.file_listbox.insert(tk.END, os.path.basename(file))
        self.file_count_var.set(f"已选择: {len(self.files)} 个文件")

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
        self.config['bitrate'] = self.bitrate_var.get()
        self.config['sample_rate'] = self.sample_rate_var.get()
        self.save_config()

    def start_conversion(self):
        """开始转换"""
        if not self.files:
            messagebox.showwarning("警告", "请先选择视频文件！")
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
        self.start_button.config(state="disabled")
        self.cancel_button.config(state="normal")

        logging.info(f"开始转换 {len(self.files)} 个文件")

        # 启动转换线程
        conversion_thread = threading.Thread(target=self.convert_files, daemon=True)
        conversion_thread.start()

    def cancel_conversion(self):
        """取消转换"""
        if messagebox.askyesno("确认", "确定要取消转换吗？"):
            self.cancel_event.set()
            self.root.after(0, lambda: self.status_var.set("正在取消..."))
            logging.info("用户请求取消转换")

    def convert_files(self):
        """转换文件（在单独的线程中运行）"""
        total_start_time = time.time()
        total_files = len(self.files)
        successful = 0
        failed = 0

        for index, file in enumerate(self.files):
            # 检查是否取消
            if self.cancel_event.is_set():
                self.root.after(0, lambda: self.status_var.set("转换已取消"))
                logging.info("转换已取消")
                break

            try:
                file_start_time = time.time()
                file_name = os.path.basename(file)

                # 更新状态（线程安全）
                self.root.after(0, lambda fn=file_name, i=index, t=total_files:
                              self.status_var.set(f"正在转换 {fn} ({i + 1}/{t})"))

                # 设置输出文件路径
                output_file = os.path.join(
                    self.output_path.get(),
                    os.path.splitext(file_name)[0] + ".mp3"
                )

                # 检查输出文件是否已存在
                if os.path.exists(output_file):
                    # 生成唯一文件名
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
                    bitrate=self.bitrate_var.get(),
                    fps=int(self.sample_rate_var.get()),
                    logger=None  # 禁用 moviepy 的进度输出
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
                    self.bitrate_var.get(),
                    self.sample_rate_var.get(),
                    timedelta(seconds=int(file_duration))
                )

                successful += 1
                logging.info(f"转换成功: {file_name} -> {os.path.basename(output_file)}")

            except Exception as e:
                failed += 1
                error_msg = f"转换 {file_name} 时出错: {str(e)}"
                logging.error(error_msg)
                self.root.after(0, lambda msg=error_msg:
                              messagebox.showerror("转换错误", msg))

        # 转换完成处理
        if not self.cancel_event.is_set():
            total_time = time.time() - total_start_time
            status_msg = f"完成: {successful} 个成功, {failed} 个失败，耗时 {timedelta(seconds=int(total_time))}"
            self.root.after(0, lambda msg=status_msg: self.status_var.set(msg))
            self.root.after(0, lambda: self.progress_var.set(100))

            # 播放完成提示音
            try:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            except:
                pass

            # 显示完成消息
            completion_msg = f"转换完成！\n\n成功: {successful} 个\n失败: {failed} 个\n总耗时: {timedelta(seconds=int(total_time))}"
            self.root.after(0, lambda msg=completion_msg:
                          messagebox.showinfo("转换完成", msg))

            logging.info(f"转换完成: 成功 {successful}, 失败 {failed}")

        # 重置状态
        self.converting = False
        self.root.after(0, lambda: self.start_button.config(state="normal"))
        self.root.after(0, lambda: self.cancel_button.config(state="disabled"))

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
    root = tk.Tk()
    app = MP4ToMP3Converter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
