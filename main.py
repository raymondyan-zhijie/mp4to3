"""MP4 to MP3 Converter - 老年人友好版
一个界面简洁、字体超大、易于操作的视频到音频转换工具

Usage: python main.py
"""

from __future__ import annotations
import sys
import tkinter as tk
import ttkbootstrap as ttk
from ui.app import MP4ToMP3ConverterApp

FONT_FAMILY = {
    "win32": "微软雅黑",
    "darwin": "PingFang SC",
}.get(sys.platform, "TkDefaultFont")


def main() -> None:
    try:
        import tkinterdnd2
        root = tkinterdnd2.Tk()
    except (ImportError, Exception):
        root = tk.Tk()

    style = ttk.Style("cosmo")
    style.configure(".", font=(FONT_FAMILY, 12))
    style.configure("TButton", font=(FONT_FAMILY, 14, "bold"))
    style.configure("TLabel", font=(FONT_FAMILY, 12))
    style.configure("TLabelframe.Label", font=(FONT_FAMILY, 16, "bold"))

    root.title("MP4 转 MP3 转换器")
    root.geometry("1000x750")

    app = MP4ToMP3ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
