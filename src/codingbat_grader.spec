# -*- mode: python -*-

import sys
from os import path
site_packages = next(p for p in sys.path if 'site-packages' in p)

block_cipher = None

a = Analysis(['codingbat_grader.py'],
             pathex=['C:\\Users\\jccooper\\Desktop\\codingbat-grader-master'],
             binaries=[],
             datas=[
               ('images', 'images')
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='CodingBat Grader',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon = 'images/icon.ico',
          version='version.txt')
