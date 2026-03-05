"""
Main application entry point for MP4 to MP3 converter
"""

import ttkbootstrap as ttk
from src.ui.main_window import MP4ToMP3MainWindow


def main():
    """Main application function"""
    # Use modern theme
    root = ttk.Window(
        title="MP4 转 MP3 转换器",
        themename="cosmo",  # Modern, clean theme
        size=(1000, 750)
    )
    
    # Set global font styles
    style = ttk.Style()
    style.configure('.', font=('微软雅黑', 12))
    style.configure('TButton', font=('微软雅黑', 14, 'bold'))
    style.configure('TLabel', font=('微软雅黑', 12))
    style.configure('TLabelframe.Label', font=('微软雅黑', 16, 'bold'))
    
    app = MP4ToMP3MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()