# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Add Conda/Python DLL paths
conda_path = os.path.dirname(sys.executable)
dll_paths = [
    conda_path,
    os.path.join(conda_path, 'Library', 'bin'),
    os.path.join(conda_path, 'DLLs')
]

a = Analysis(
    ['imageMain.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('cv2'),
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'cv2',
        'numpy',
        'PIL',
        'PIL._imaging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add DLLs from Conda environment
for dll_path in dll_paths:
    if os.path.exists(dll_path):
        a.datas += [(os.path.join('lib', os.path.basename(f)), f, 'DATA')
                   for f in os.listdir(dll_path) if f.endswith('.dll')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ImageStitcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico' if os.path.exists('app_icon.ico') else None,
    version='file_version_info.txt' if os.path.exists('file_version_info.txt') else None,
    uac_admin=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ImageStitcher',
) 