# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集数据文件和元数据
datas = []
datas += collect_data_files('ttkbootstrap')
datas += collect_data_files('imageio', include_py_files=False)
datas += collect_data_files('imageio_ffmpeg', include_py_files=False)

# 收集包的元数据（重要！）
try:
    from PyInstaller.utils.hooks import copy_metadata
    datas += copy_metadata('imageio')
    datas += copy_metadata('imageio_ffmpeg')
    datas += copy_metadata('moviepy')
    datas += copy_metadata('ttkbootstrap')
except:
    pass

# 收集所有隐藏导入
hiddenimports = []
hiddenimports += collect_submodules('moviepy')
hiddenimports += collect_submodules('ttkbootstrap')
hiddenimports += collect_submodules('imageio')
hiddenimports += collect_submodules('imageio_ffmpeg')
hiddenimports += ['PIL._tkinter_finder']

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas'],  # 排除不需要的大型库
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MP4toMP3Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果有图标文件，可以在这里指定路径
)
