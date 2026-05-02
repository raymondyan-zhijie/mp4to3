# MP4 to MP3 Converter - 老年人友好版

[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2B-0078D6?style=flat&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个专为老年人设计的视频到音频转换工具，界面简洁、字体超大、操作简单。

## ✨ 功能特点

### 🎨 老年人友好设计
- 🖥️ **自动最大化窗口** - 启动即全屏，充分利用屏幕空间
- 📏 **超大字体** - 标题24号，按钮14号粗体，易于阅读
- 🔘 **超大按钮** - 大号按钮，容易点击，不会误触
- 🎯 **三步操作** - 选择视频 → 设置选项 → 开始转换，简单明了
- 📜 **滚动条支持** - 支持鼠标滚轮，内容完整显示
- 🌈 **现代配色** - Cosmo主题，清新明快，高对比度

### 🎵 强大功能
- 🎬 **批量转换** - 同时选择和转换多个视频文件
- 🖱️ **拖放支持** - 从文件管理器直接拖入视频文件，对老年用户极友好
- 🎵 **高质量音频** - 支持多种比特率（128k - 320k），默认推荐192k
- 📁 **灵活输出** - 自定义输出目录，默认保存至用户音乐文件夹
- 📊 **实时进度** - 实时显示转换进度和状态
- 📝 **历史记录** - SQLite 存储所有转换历史，支持查询和清空
- 🎯 **多格式支持** - 支持 MP4、AVI、MKV、MOV、FLV、WMV、WebM、TS/MTS
- ⏸️ **取消功能** - 可随时中止正在进行的转换任务
- 🔔 **完成提示** - 转换完成后自动声音提醒
- 📋 **详细日志** - 记录所有操作和错误信息，便于问题排查
- 💾 **配置保存** - TOML 格式自动保存用户偏好设置（音质、输出目录）
- 🛡️ **安全防护** - 文件存在性检查、格式验证、ffmpeg 进程管理

## 💻 系统要求

- **操作系统**: Windows 10 或更高版本
- **屏幕分辨率**: 建议 1280x720 或更高
- **磁盘空间**: 至少 100MB 可用空间

## 📦 安装说明

### 方式一：直接使用（推荐）

1. 下载最新版本的 `MP4toMP3Converter.exe` 可执行文件
2. 双击运行，无需安装
3. Windows 可能会提示安全警告，选择"仍要运行"

### 方式二：从源代码运行

```bash
# 1. 克隆仓库
git clone https://github.com/raymondyan-zhijie/mp4to3.git
cd mp4to3

# 2. 安装运行时依赖
pip install imageio-ffmpeg ttkbootstrap tkinterdnd2 platformdirs tomli-w

# 3. 运行程序
python main.py
```

或直接双击 `run.bat` 文件。

### 方式三：开发环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/raymondyan-zhijie/mp4to3.git
cd mp4to3

# 2. 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 3. 安装全部依赖（含打包工具）
pip install -r requirements.txt

# 4. 运行
python main.py
```

## 🚀 使用指南

### 基本操作（三步完成）

#### 第一步：选择视频文件
1. 点击 **"📁 选择视频文件"** 按钮
2. 选择一个或多个视频文件（支持多选）
3. 文件会显示在列表中，自动过滤不支持的格式

#### 第二步：设置转换选项（可选）
- **音质选择**：推荐使用 "192k - 高质量 ★推荐"
  - 128k - 普通质量（文件小）
  - 192k - 高质量（推荐，平衡质量和大小）
  - 256k - 极高质量
  - 320k - 最高质量（文件大）
- **保存位置**：默认保存到"我的音乐"文件夹，可点击"更改位置"自定义

#### 第三步：开始转换
1. 点击 **"🚀 开始转换"** 按钮
2. 等待进度条完成（会显示当前转换的文件名）
3. 转换完成后会听到提示音，并显示结果

### 高级功能

#### 查看历史记录
- 点击底部的 **"📋 查看转换历史"** 按钮
- 可查看所有转换记录（时间、文件名、音质、耗时）
- 可点击"清空历史"删除所有记录

#### 取消转换
- 转换过程中，点击 **"⏹️ 取消转换"** 按钮
- 确认后会停止当前转换

#### 使用滚动条
- 如果窗口缩小，内容显示不全
- 使用右侧滚动条或鼠标滚轮滚动查看

## 🛠️ 打包为可执行文件

### 使用构建脚本（推荐）
```batch
build.bat
```

### 手动打包
```bash
pip install pyinstaller>=5.0.0
pyinstaller build.spec
```

打包后的可执行文件位于 `dist\MP4toMP3Converter.exe`。

> **注意**：打包前请确保已安装 `requirements.txt` 中的所有依赖。

## 📂 项目结构

```
mp4to3/
├── main.py                     # 入口文件（~30 行）
├── core/                       # 核心业务逻辑层（零 UI 依赖）
│   ├── models.py               # 数据类定义（ConversionConfig, ConversionTask 等）
│   ├── config.py               # TOML 配置管理（自动从 JSON 迁移）
│   ├── history.py              # SQLite 历史存储（自动从 JSON 迁移）
│   └── engine.py               # FFmpeg 子进程转换器（替代 moviepy）
├── ui/                         # 界面层
│   ├── widgets.py              # 可复用组件（ScrollableFrame, DnDListbox）
│   └── app.py                  # 主应用窗口（纯 UI，委托核心层）
├── requirements.txt            # Python 依赖列表（含运行时和打包依赖）
├── build.spec                  # PyInstaller 打包配置
├── build.bat                   # 一键构建脚本
├── run.bat                     # 开发环境运行脚本
├── README.md                   # 项目说明文档
├── .gitignore                  # Git 忽略文件配置
└── LICENSE                     # MIT 许可证
```

### 运行时自动生成
程序运行后会在 `%APPDATA%\MP4to3\` 目录下自动生成：
- `conversion_history.json` - 转换历史记录
- `config.json` - 用户配置文件
- `converter.log` - 日志文件

## 🐛 常见问题

### Q: 为什么窗口这么大？
**A:** 专为老年人设计，默认最大化窗口，字体和按钮都很大，方便老花眼用户使用。

### Q: 如何缩小窗口？
**A:** 点击窗口右上角的"还原"按钮，可以缩小窗口。窗口最小尺寸为 800x600。

### Q: 内容显示不全怎么办？
**A:** 使用右侧的滚动条或鼠标滚轮滚动查看。建议保持窗口最大化使用。

### Q: 转换速度很慢？
**A:** 转换速度取决于文件大小、视频时长和选择的音质。高比特率会增加处理时间。

### Q: 支持哪些视频格式？
**A:** 支持以下常见视频格式：MP4、AVI、MKV、MOV、FLV、WMV、M4V、WebM、TS、MTS。

### Q: 转换失败怎么办？
**A:** 常见原因和解决方法：
1. **源文件损坏或格式不受支持** - 尝试用视频播放器确认文件可正常播放
2. **输出目录没有写入权限** - 更换输出目录或检查权限设置
3. **磁盘空间不足** - 清理磁盘后重试
4. **视频文件没有音频轨道** - 确认源视频包含音频

查看详细错误日志：
- Windows: `%APPDATA%\MP4to3\converter.log`

### Q: 如何卸载程序？
**A:**
1. 删除可执行文件 `MP4toMP3Converter.exe`
2. 如需删除配置和历史记录，删除文件夹：`%APPDATA%\MP4to3\`

### Q: 程序安全吗？
**A:** 完全安全，开源代码可在 GitHub 查看。Windows 可能会提示"未知发布者"，这是因为没有购买代码签名证书，可以放心运行。

## 📝 更新日志

### v3.0.0 (架构重构)
- 🏗️ **分层架构** - 核心层与 UI 完全解耦，`core/` 零 UI 依赖
- 🔧 **FFmpeg 替代 moviepy** - 直接调用内置 ffmpeg，减少依赖体积
- 🖱️ **拖放支持** - 从文件管理器直接拖入视频文件
- 💾 **TOML 配置** - 类型安全 dataclass + TOML，自动从 JSON 迁移
- 🗄️ **SQLite 历史** - 标准库内置，自动从 JSON 迁移
- 🌍 **跨平台路径** - platformdirs 替代硬编码 %APPDATA%

### v2.0.1
- 🛡️ 添加文件存在性检查，防止源文件被删除后崩溃
- 🛡️ 添加 try-finally 资源保护，确保异常时正确释放音视频资源
- 🛡️ 添加文件格式白名单验证，拒绝不支持的文件格式
- 🛡️ 添加文件大小检查（拒绝0字节文件）
- 🛡️ 使用精确异常类型替代裸 Exception
- 📝 改进项目文档结构

### v2.0.0 (老年人友好版)
- ✨ **全新现代化界面** - 使用 ttkbootstrap 主题库
- 🖥️ **自动最大化窗口** - 启动即全屏
- 📏 **超大字体和按钮** - 专为老年人设计
- 📜 **添加滚动条** - 支持鼠标滚轮，内容完整显示
- 🎯 **简化操作流程** - 三步完成转换
- 🌈 **高对比度配色** - Cosmo 主题，清晰易读
- 🔧 **优化布局** - 紧凑设计，充分利用屏幕空间
- 💾 **配置自动保存** - 记住用户偏好设置
- 📋 **改进历史记录** - 独立窗口显示，更清晰

### v1.5.0
- ✅ 完整中文化界面
- ✅ 添加取消转换功能
- ✅ 支持更多视频格式
- ✅ 改进错误处理和日志记录
- ✅ 优化线程安全性
- ✅ 修复 moviepy 2.x 兼容性问题

### v1.0.0
- 🎉 初始版本发布
- 基本的 MP4 到 MP3 转换功能
- 批量处理支持
- 历史记录功能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发约定
- 代码风格遵循 PEP 8
- 提交信息使用约定式提交格式：`类型: 描述`（如 `feat:`、`fix:`、`docs:`）
- 重大更改前请先提交 Issue 讨论

## 👨‍💻 技术栈

- **Python 3.11+** - 核心语言
- **FFmpeg** (via imageio-ffmpeg) - 视频音频处理引擎（替代 moviepy）
- **ttkbootstrap** - 现代化 UI 主题框架
- **Tkinter** - Python 标准 GUI 库
- **tkinterdnd2** - 拖放文件支持
- **SQLite** - 标准库历史记录存储
- **TOML** - 配置文件格式（tomllib + tomli-w）
- **platformdirs** - 跨平台数据目录
- **PyInstaller** - 可执行文件打包工具

### 架构特色
- **分层解耦**：`core/` 层零 UI 依赖，未来添加 CLI 或 Web 界面只需替换 `ui/` 层
- **FFmpeg 直调**：通过 `subprocess` 直接调用内置 ffmpeg，消除 moviepy 依赖
- **类型安全配置**：dataclass + TOML，IDE 自动补全

## 🙏 鸣谢

- [FFmpeg](https://ffmpeg.org/) - 业界标准的音视频处理工具
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) - 内置 ffmpeg 二进制分发
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) - 现代化的 Tkinter 主题
- [tkinterdnd2](https://github.com/Eliav2/tkinterdnd2) - Tkinter 拖放支持

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**💝 献给所有需要简单易用工具的老年用户**
