"""MP4 to MP3 Converter - 老年人友好版
一个界面简洁、字体超大、易于操作的视频到音频转换工具

Usage: python main.py
"""

from __future__ import annotations
import tkinter as tk
import ttkbootstrap as ttk
from ui.app import MP4ToMP3ConverterApp


def main() -> None:
    try:
        import tkinterdnd2
        root = tkinterdnd2.Tk()
    except (ImportError, Exception):
        root = tk.Tk()

    style = ttk.Style("cosmo")
    style.configure(".", font=("微软雅黑", 12))
    style.configure("TButton", font=("微软雅黑", 14, "bold"))
    style.configure("TLabel", font=("微软雅黑", 12))
    style.configure("TLabelframe.Label", font=("微软雅黑", 16, "bold"))

    root.title("MP4 转 MP3 转换器")
    root.geometry("1000x750")

    app = MP4ToMP3ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
