
# native imports
import subprocess  # nosec: B404
from pathlib import Path


def clean_up() -> None:
  '''
  move all *.pyd files to lib
  move all *.dll except python3*.dll to lib
  remove *.dist-info folders
  Set Hidden attribute for unwanted files/folders
  '''
  dist_path: Path = Path('.') / 'dist' / 'StreamChatWars'
  lip_path: Path = dist_path / 'lib'
  lip_path.mkdir(exist_ok=True)
  keep_files: list[str] = [
    'base_library.zip',
    'StreamChatWars.exe',
    'python38.dll',
    'python39.dll',
    'python310.dll',
    'python311.dll',
    'python312.dll',
    "SDL2.dll",  # pygame
    "SDL2_image.dll",  # pygame
    "SDL2_mixer.dll",  # pygame
    "SDL2_ttf.dll",  # pygame
  ]
  for p in dist_path.iterdir():
    if p.is_file() and p.name not in keep_files:
      p.rename(lip_path / p.name)
    if p.is_dir() and p.name.endswith('dist-info'):
      p.rename(lip_path / p.name)
  # hide files/folders
  all_files = str(dist_path / '*')
  exe_file = str(dist_path / 'StreamChatWars.exe')
  data_folder = str(dist_path / 'data')
  attrib_exe = str(Path('C:/') / 'Windows' / 'System32' / 'attrib.exe')
  subprocess.run(
    [attrib_exe, '+H', all_files, '/D'], shell=False  # nosec: B603
  )
  subprocess.run(
    [attrib_exe, '-H', exe_file], shell=False  # nosec: B603
  )
  subprocess.run(
    [attrib_exe, '-H', data_folder, '/D'], shell=False  # nosec: B603
  )
