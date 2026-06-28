# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path.cwd()
block_cipher = None

a = Analysis(
    [str(root / 'src' / 'ig_baixador' / '__main__.py')],
    pathex=[str(root / 'src')],
    binaries=[],
    datas=[(str(root / 'bin' / 'win'), 'bin/win')],
    hiddenimports=[],
    hookspath=[], runtime_hooks=[], excludes=[],
    cipher=block_cipher, noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='IG-Baixador',
    debug=False, bootloader_ignore_signals=False, strip=False,
    upx=False, runtime_tmpdir=None, console=False,
)
