# -*- mode: python ; coding: utf-8 -*-

# native imports
import sys
from os import environ
from pathlib import Path

# pip imports
from PyInstaller.building.build_main import COLLECT
from PyInstaller.building.build_main import EXE
from PyInstaller.building.build_main import PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.build_main import Tree
from PyInstaller.compat import is_venv
from PyInstaller.utils.hooks import collect_submodules


sys.path.append(str(Path('.').absolute()))  # required to make import work

# local imports
from install_hooks.post_install import clean_up  # noqa: E402


if not is_venv:
  print("Building only works from virtual environments!")
  sys.exit(1)

block_cipher = None

binaries = [
  (
    Path(environ['VIRTUAL_ENV']) / 'Lib' / 'site-packages' / 'vgamepad' / 'win'
    / 'vigem' / 'client' / 'x64' / 'ViGEmClient.dll',
    'vgamepad/win/vigem/client/x64'
  ),
  (
    Path(environ['VIRTUAL_ENV']) / 'Lib' / 'site-packages' / 'vgamepad' / 'win'
    / 'vigem' / 'client' / 'x86' / 'ViGEmClient.dll',
    'vgamepad/win/vigem/client/x86'
  ),
]

extra_folders = (
  Tree('./data/', prefix='data', excludes=['.gitignore', 'session'])
)

# required to make collect_submodules work
environ['PYTHONPATH'] = str(Path('.').absolute())

hidden_imports = (
  collect_submodules('streamchatwars.actionsets.subclasses')
  + collect_submodules('streamchatwars.teams.subclasses')
)

if not hidden_imports:
  raise ImportError(
    "PyInstaller broke collect_submodules()! "
    "Failed to import individual actionsets and teams"
  )

a = Analysis(
  ['__run_streamchatwars__.py'],
  pathex=[],
  binaries=binaries,
  datas=[],
  hiddenimports=hidden_imports,
  hookspath=[],
  hooksconfig={},
  runtime_hooks=['install_hooks/runtime.py'],
  excludes=[],
  win_no_prefer_redirects=False,
  win_private_assemblies=False,
  cipher=block_cipher,
  noarchive=False
)

pyz = PYZ(
  a.pure,
  a.zipped_data,
  cipher=block_cipher
)

exe = EXE(
  pyz,
  a.scripts,
  [],
  exclude_binaries=True,
  name='StreamChatWars',
  debug=False,
  bootloader_ignore_signals=False,
  strip=False,
  upx=True,
  console=True,
  disable_windowed_traceback=False,
  target_arch=None,
  codesign_identity=None,
  entitlements_file=None
)

coll = COLLECT(
  exe,
  a.binaries,
  a.zipfiles,
  a.datas + extra_folders,
  strip=False,
  upx=True,
  upx_exclude=[],
  name='StreamChatWars'
)

clean_up()
