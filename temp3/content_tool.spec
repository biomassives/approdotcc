# content_tool.spec
# PyInstaller spec file to bundle content_ux.py into a standalone executable.
# Usage: pyinstaller content_tool.spec

# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Path to your main script
script_path = 'content_ux.py'

# Collect all tkinter dynamic libraries, if needed
hidden_imports = collect_submodules('tkinter') + collect_submodules('tkinter.ttk')

a = Analysis(
    [script_path],
    pathex=[],  # optional: add extra search paths
    binaries=[],
    datas=[
        # Include your icon or any data files
        ('icon.png', '.'),  # if you have a custom icon
        ('content_tool.py', '.'),  # include CLI script for wizard
    ] + collect_data_files('tkinter'),
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=None,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ContentManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # set to True for console window
    icon='icon.png'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='ContentManager'
)

