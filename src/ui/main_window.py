"""
Main window for MP4 to MP3 converter application
Implements the elderly-friendly UI using ttkbootstrap
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import time
from datetime import timedelta
import winsound
import threading
from pathlib import Path
from typing import List

# Import core components
from src.core.converter import MP4ToMP3ConverterCore
from src.utils.config_manager import ConfigManager
from src.utils.history_manager import HistoryManager


class MP4ToMP3MainWindow:
    """Main application window - Elderly-friendly MP4 to MP3 converter"""
    
    def __init__(self, root):
        """Initialize the converter application"""
        self.root = root
        self.root.title("MP4 转 MP3 转换器")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Maximize window (elderly-friendly)
        self.root.state('zoomed')
        
        # Set minimum window size
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        
        # Store screen dimensions for responsive adjustments
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize core components
        self.converter = MP4ToMP3ConverterCore()
        self.config_manager = ConfigManager()
        self.history_manager = HistoryManager()
        
        # File list
        self.files = []
        
        # Conversion parameters
        self.bitrates = ["128k - 普通质量", "192k - 高质量 ★推荐", "256k - 极高质量", "320k - 最高质量"]
        self.bitrate_values = ["128k", "192k", "256k", "320k"]
        
        # Create UI
        self.create_widgets()
        
        # Apply saved configuration
        self.apply_config()
        
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create all UI components"""
        # Create scrollable container
        # Outer container
        container_outer = ttk.Frame(self.root)
        container_outer.pack(fill=BOTH, expand=YES)
        
        # Create Canvas and Scrollbar
        canvas = tk.Canvas(container_outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_outer, orient=VERTICAL, command=canvas.yview)
        
        # Scrollable main frame
        main_container = ttk.Frame(canvas, padding=20)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Add main container to canvas
        canvas_frame = canvas.create_window((0, 0), window=main_container, anchor=NW)
        
        # Configure scroll region
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Ensure frame width fills canvas
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(canvas_frame, width=canvas_width)
        
        main_container.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Mouse wheel support
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Store canvas references for later use
        self.canvas = canvas
        self.main_container = main_container
        
        # ==================== Title Area ====================
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
        
        # ==================== Step 1: Select Files ====================
        step1_frame = ttk.Labelframe(
            main_container,
            text="  第一步：选择要转换的视频文件  ",
            padding=15,
            bootstyle="primary"
        )
        step1_frame.pack(fill=BOTH, expand=YES, pady=(0, 12))
        
        # Button container
        button_container = ttk.Frame(step1_frame)
        button_container.pack(fill=X, pady=(0, 12))
        
        # Select files button (large)
        self.select_btn = ttk.Button(
            button_container,
            text="📁 选择视频文件",
            command=self.select_files,
            bootstyle="success",
            width=20
        )
        self.select_btn.pack(side=LEFT, padx=(0, 10))
        self.select_btn.configure(padding=12)
        
        # Clear button
        self.clear_btn = ttk.Button(
            button_container,
            text="🗑️ 清空列表",
            command=self.clear_files,
            bootstyle="secondary-outline",
            width=15
        )
        self.clear_btn.pack(side=LEFT)
        self.clear_btn.configure(padding=12)
        
        # File count display
        self.file_count_var = tk.StringVar(value="尚未选择文件")
        count_label = ttk.Label(
            button_container,
            textvariable=self.file_count_var,
            font=("微软雅黑", 16, "bold"),
            bootstyle="info"
        )
        count_label.pack(side=LEFT, padx=(20, 0))
        
        # File list (larger font)
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
        
        # ==================== Step 2: Settings ====================
        step2_frame = ttk.Labelframe(
            main_container,
            text="  第二步：设置转换选项（可选）  ",
            padding=15,
            bootstyle="info"
        )
        step2_frame.pack(fill=X, pady=(0, 12))
        
        # Quality selection
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
        
        # Output directory
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
        
        # ==================== Step 3: Start Conversion ====================
        step3_frame = ttk.Labelframe(
            main_container,
            text="  第三步：开始转换  ",
            padding=15,
            bootstyle="success"
        )
        step3_frame.pack(fill=X, pady=(0, 12))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            step3_frame,
            variable=self.progress_var,
            maximum=100,
            bootstyle="success-striped",
            length=400
        )
        self.progress_bar.pack(fill=X, pady=(0, 15))
        
        # Status display
        self.status_var = tk.StringVar(value="准备就绪，请选择视频文件")
        status_label = ttk.Label(
            step3_frame,
            textvariable=self.status_var,
            font=("微软雅黑", 14),
            bootstyle="secondary",
            anchor=CENTER
        )
        status_label.pack(fill=X, pady=(0, 15))
        
        # Convert button (large, prominent)
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
        
        # ==================== History Button ====================
        history_btn = ttk.Button(
            main_container,
            text="📋 查看转换历史",
            command=self.show_history,
            bootstyle="secondary-outline",
            width=20
        )
        history_btn.pack(pady=(10, 0))
        history_btn.configure(padding=10)
    
    def apply_config(self):
        """Apply saved configuration to UI"""
        # Set bitrate
        bitrate = self.config_manager.get('bitrate', '192k')
        try:
            index = self.bitrate_values.index(bitrate)
            self.bitrate_var.set(self.bitrates[index])
        except ValueError:
            self.bitrate_var.set(self.bitrates[1])  # Default to 192k
        
        self.output_path.set(self.config_manager.get('output_dir', os.path.expanduser("~\\Music")))
    
    def select_files(self):
        """Select files to convert"""
        files = filedialog.askopenfilenames(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4;*.avi;*.mkv;*.mov;*.flv;*.wmv;*.m4v"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            # Avoid duplicate additions
            for file in files:
                if file not in self.files:
                    self.files.append(file)
            self.update_file_list()
    
    def clear_files(self):
        """Clear file selection"""
        self.files.clear()
        self.update_file_list()
    
    def update_file_list(self):
        """Update file list display"""
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
        """Select output directory"""
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.output_path.get()
        )
        if directory:
            # Validate directory exists
            if not os.path.exists(directory):
                messagebox.showerror("错误", "所选目录不存在！")
                return
            
            # Validate write permissions
            if not os.access(directory, os.W_OK):
                messagebox.showerror("错误", "所选目录没有写入权限！")
                return
            
            self.output_path.set(directory)
            self.config_manager.set('output_dir', directory)
    
    def on_settings_changed(self, event=None):
        """Save settings when they change"""
        # Get actual bitrate value
        selected = self.bitrate_var.get()
        try:
            index = self.bitrates.index(selected)
            self.config_manager.set('bitrate', self.bitrate_values[index])
        except ValueError:
            pass
    
    def start_conversion(self):
        """Start conversion process"""
        if not self.files:
            messagebox.showwarning("提示", "请先选择视频文件！\n\n点击【选择视频文件】按钮来选择要转换的文件。")
            return
        
        # Validate output directory
        output_dir = self.output_path.get()
        if not os.path.exists(output_dir):
            messagebox.showerror("错误", "输出目录不存在！")
            return
        
        if self.converter.converting:
            return
        
        # Reset cancel flag
        self.converter.reset_cancel_flag()
        
        self.converter.converting = True
        self.start_button.config(state=DISABLED)
        self.cancel_button.config(state=NORMAL)
        self.select_btn.config(state=DISABLED)
        self.clear_btn.config(state=DISABLED)
        
        # Start conversion thread
        conversion_thread = threading.Thread(target=self.run_conversion, daemon=True)
        conversion_thread.start()
    
    def cancel_conversion(self):
        """Cancel conversion"""
        if messagebox.askyesno("确认", "确定要取消转换吗？"):
            self.converter.cancel_current_operation()
            self.root.after(0, lambda: self.status_var.set("正在取消转换..."))
    
    def run_conversion(self):
        """Run the conversion process in a separate thread"""
        # Get actual bitrate value
        selected = self.bitrate_var.get()
        try:
            index = self.bitrates.index(selected)
            bitrate = self.bitrate_values[index]
        except ValueError:
            bitrate = "192k"
        
        # Define callback functions for progress and status updates
        def progress_callback(progress):
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
        
        def status_callback(status):
            self.root.after(0, lambda s=status: self.status_var.set(s))
        
        # Run the conversion
        stats = self.converter.convert_files(
            input_files=self.files,
            output_dir=self.output_path.get(),
            bitrate=bitrate,
            progress_callback=progress_callback,
            status_callback=status_callback
        )
        
        # Handle completion
        if not stats['cancelled']:
            # Play completion sound
            try:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            except:
                pass
            
            # Show completion message
            completion_msg = (
                f"🎉 转换完成！\n\n"
                f"✅ 成功：{stats['successful']} 个\n"
                f"❌ 失败：{stats['failed']} 个\n"
                f"⏱️ 总耗时：{timedelta(seconds=int(stats['total_time']))}\n\n"
                f"文件已保存到：\n{self.output_path.get()}"
            )
            self.root.after(0, lambda msg=completion_msg:
                          messagebox.showinfo("转换完成", msg))
        
        # Add successful conversions to history
        for file in self.files:
            input_filename = os.path.basename(file)
            output_filename = os.path.splitext(input_filename)[0] + ".mp3"
            output_path = os.path.join(self.output_path.get(), output_filename)
            
            # Handle potential duplicate names
            counter = 1
            original_output_path = output_path
            while os.path.exists(output_path):
                base_name = os.path.splitext(input_filename)[0]
                output_path = os.path.join(
                    self.output_path.get(),
                    f"{base_name}_{counter}.mp3"
                )
                counter += 1
            
            # Add to history if the file was actually created
            if os.path.exists(output_path):
                self.history_manager.add_record(
                    source_file=file,
                    output_file=output_path,
                    bitrate=bitrate,
                    duration=str(timedelta(seconds=int(stats['total_time'])))
                )
        
        # Reset UI state
        self.converter.converting = False
        self.root.after(0, lambda: self.start_button.config(state=NORMAL))
        self.root.after(0, lambda: self.cancel_button.config(state=DISABLED))
        self.root.after(0, lambda: self.select_btn.config(state=NORMAL))
        self.root.after(0, lambda: self.clear_btn.config(state=NORMAL))
        
        # Update status
        if stats['cancelled']:
            status_msg = "❌ 转换已取消"
        else:
            status_msg = f"✅ 转换完成！成功 {stats['successful']} 个，失败 {stats['failed']} 个，耗时 {timedelta(seconds=int(stats['total_time']))}"
        
        self.root.after(0, lambda msg=status_msg: self.status_var.set(msg))
        self.root.after(0, lambda: self.progress_var.set(100))
    
    def show_history(self):
        """Show history window"""
        history_window = ttk.Toplevel(self.root)
        history_window.title("转换历史记录")
        history_window.geometry("900x600")
        
        # Main container
        container = ttk.Frame(history_window, padding=20)
        container.pack(fill=BOTH, expand=YES)
        
        # Title
        title = ttk.Label(
            container,
            text="📋 转换历史记录",
            font=("微软雅黑", 20, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=(0, 20))
        
        # Button frame
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
        
        # History list
        history_records = self.history_manager.get_history()
        if history_records:
            # Use text box to display history (more readable)
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
            
            # Populate history records
            for i, item in enumerate(reversed(history_records), 1):
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
        """Clear history and refresh window"""
        if messagebox.askyesno('确认', '确定要清空所有转换历史记录吗？', parent=window):
            self.history_manager.clear_history()
            window.destroy()
            self.show_history()
    
    def on_closing(self):
        """Handle window closing event"""
        if self.converter.converting:
            if messagebox.askokcancel("退出", "转换正在进行中，确定要退出吗？"):
                self.converter.cancel_current_operation()
                self.root.destroy()
        else:
            self.root.destroy()