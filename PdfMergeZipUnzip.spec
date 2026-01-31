# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['PdfMergeZipUnzip.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.ico', '.'), ('C:\\Users\\Ramchandra\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\customtkinter', 'customtkinter/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PdfMergeZipUnzip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir='.',
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
