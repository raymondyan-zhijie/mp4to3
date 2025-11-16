# MP4 to MP3 Converter

一个功能强大、界面友好的 Windows 桌面应用程序，用于将视频文件批量转换为 MP3 音频格式。

## ✨ 功能特点

- 🎬 **批量转换** - 同时选择和转换多个视频文件
- 🎵 **高质量音频** - 支持多种比特率（128k - 320k）和采样率（44.1kHz - 96kHz）
- 📁 **灵活输出** - 自定义输出目录，默认保存至用户音乐文件夹
- 📊 **实时进度** - 实时显示转换进度和状态
- 📝 **历史记录** - 自动记录所有转换历史，支持搜索和过滤
- 🎨 **现代界面** - 简洁直观的图形用户界面
- 🎯 **多格式支持** - 支持 MP4、AVI、MKV、MOV、FLV 等常见视频格式
- ⏸️ **取消功能** - 可随时中止正在进行的转换任务
- 🔔 **完成提示** - 转换完成后自动声音提醒
- 📋 **详细日志** - 记录所有操作和错误信息，便于问题排查

## 💻 系统要求

- **操作系统**: Windows 10 或更高版本
- **Python**: 3.7+ （仅开发环境需要）
- **磁盘空间**: 至少 100MB 可用空间

## 📦 安装说明

### 方式一：直接使用（推荐）

下载最新版本的 `MP4toMP3Converter.exe` 可执行文件，双击即可运行，无需安装。

### 方式二：从源代码运行

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/mp4to3.git
cd mp4to3
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python main.py
```

## 🚀 使用指南

### 基本操作

1. **选择文件**
   - 点击 "Select Files" 按钮选择要转换的视频文件
   - 支持多选，可一次性添加多个文件
   - 点击 "Clear Selection" 清空文件列表

2. **设置参数**
   - **Bitrate（比特率）**: 音频质量，越高质量越好，文件也越大
     - 128k: 标准质量
     - 192k: 高质量（推荐）
     - 256k: 极高质量
     - 320k: 最高质量
   - **Sample Rate（采样率）**: 音频采样频率
     - 44100 Hz: CD 音质（推荐）
     - 48000 Hz: 专业音质
     - 96000 Hz: 高保真音质

3. **选择输出目录**
   - 点击 "Browse" 按钮选择输出文件夹
   - 默认保存到 "我的音乐" 文件夹

4. **开始转换**
   - 点击 "Start Conversion" 按钮开始转换
   - 实时查看转换进度和状态
   - 转换过程中可点击 "Cancel" 按钮中止

5. **查看历史**
   - 切换到 "历史记录" 标签页
   - 查看所有转换记录
   - 使用搜索框过滤记录
   - 点击 "Clear History" 清空所有记录

### 高级功能

- **配置保存**: 程序会自动保存您的偏好设置（比特率、采样率、输出目录）
- **错误处理**: 单个文件转换失败不会影响其他文件的转换
- **日志记录**: 所有操作记录保存在 `converter.log` 文件中

## 🛠️ 打包为可执行文件

如果您想自己打包程序：

```bash
# 确保已安装 PyInstaller
pip install pyinstaller

# 使用提供的配置文件打包
pyinstaller build.spec

# 或使用命令行打包
pyinstaller --onefile --windowed --icon=icon.ico --name=MP4toMP3Converter main.py
```

打包后的可执行文件位于 `dist` 目录下。

## 📂 文件说明

```
mp4to3/
├── main.py                    # 主程序文件
├── requirements.txt           # Python 依赖列表
├── build.spec                # PyInstaller 打包配置
├── README.md                 # 项目说明文档
├── .gitignore               # Git 忽略文件配置
├── conversion_history.json  # 转换历史记录（自动生成）
├── config.json              # 用户配置文件（自动生成）
└── converter.log            # 日志文件（自动生成）
```

## 🐛 常见问题

**Q: 为什么转换速度很慢？**
A: 转换速度取决于文件大小、视频时长和您选择的音频质量。高比特率和高采样率会增加处理时间。

**Q: 支持哪些视频格式？**
A: 支持所有 moviepy 库能处理的格式，包括 MP4、AVI、MKV、MOV、FLV、WMV 等。

**Q: 转换失败怎么办？**
A: 请检查 `converter.log` 文件查看详细错误信息。常见原因包括：
- 源文件损坏或格式不受支持
- 输出目录没有写入权限
- 磁盘空间不足

**Q: 如何卸载程序？**
A: 直接删除可执行文件即可。如需删除配置和历史记录，请同时删除 `conversion_history.json` 和 `config.json`。

## 📝 更新日志

### v2.0.0 (最新)
- ✅ 添加取消转换功能
- ✅ 支持更多视频格式
- ✅ 改进错误处理和日志记录
- ✅ 添加配置文件自动保存
- ✅ 优化线程安全性
- ✅ 改进用户界面

### v1.0.0
- 🎉 初始版本发布
- 基本的 MP4 到 MP3 转换功能
- 批量处理支持
- 历史记录功能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 👨‍💻 作者

您的名字

## 🙏 鸣谢

- [MoviePy](https://zulko.github.io/moviepy/) - 强大的视频处理库
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Python 标准 GUI 库
