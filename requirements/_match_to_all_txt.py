'''
Script that reads requirements from all.txt and updates versions in
core|dev|build[-dep].txt.

Will NOT add aditional dependencies!
'''

# native imports
from pathlib import Path

# pip imports
import colorama
from colorama import Fore
from pkg_resources import Requirement
from pkg_resources import parse_requirements


# paths
FILE_ALL: Path = Path(__file__).parent / 'all.txt'
FILE_CORE: Path = Path(__file__).parent / 'core.txt'
FILE_CORE_DEP: Path = Path(__file__).parent / 'core-dep.txt'
FILE_DEV: Path = Path(__file__).parent / 'dev.txt'
FILE_DEV_DEP: Path = Path(__file__).parent / 'dev-dep.txt'
FILE_BUILD: Path = Path(__file__).parent / 'build.txt'
FILE_BUILD_DEP: Path = Path(__file__).parent / 'build-dep.txt'


def parse_requirement_contents(contents: str) -> dict[str, Requirement]:
  return {
    req.key: req for req in parse_requirements(contents)
  }


def load_requirement_txt(path: Path | str) -> dict[str, Requirement]:
  path = Path(path)
  return parse_requirement_contents(path.read_text())


def load_all_txt() -> dict[str, Requirement]:
  return load_requirement_txt(FILE_ALL)


def update_requirement_txt(path: Path | str) -> None:
  path = Path(path)
  all_reqs: dict[str, Requirement] = load_all_txt()
  with path.open('r+', encoding='utf-8') as file:
    contents: str = file.read()
    file_reqs: dict[str, Requirement] = parse_requirement_contents(contents)
    has_changes: bool = False
    for key, req_in_file in file_reqs.items():
      req_in_all: Requirement | None = all_reqs.get(key, None)
      if req_in_all is None:
        # Requirement doesn not exist in all.txt !! Obsolete dependency?
        print(
          f"{Fore.RED}[{Fore.CYAN}{path.name}{Fore.RED}] Dependency "
          f"{Fore.MAGENTA}{req_in_file.project_name}{Fore.RED} missing in "
          f"all.txt{Fore.RESET}"
        )
        continue
      if req_in_file.specs != req_in_all.specs:
        # Outdated dependency, update
        print(
          f"{Fore.YELLOW}[{Fore.CYAN}{path.name}{Fore.YELLOW}] Dependency "
          f"mismatch in {Fore.MAGENTA}{req_in_file.project_name}{Fore.YELLOW}, "
          f"updating from {Fore.LIGHTBLUE_EX}{str(req_in_file)}{Fore.YELLOW} "
          f"to {Fore.LIGHTBLUE_EX}{str(req_in_all)}{Fore.RESET}"
        )
        contents = contents.replace(str(req_in_file), str(req_in_all))
        has_changes = True

    if has_changes:
      file.seek(0)
      file.write(contents)
      file.truncate()
    else:
      print(
        f"{Fore.GREEN}[{Fore.CYAN}{path.name}{Fore.GREEN}] Dependencies "
        f"match. :){Fore.RESET}"
      )


def update_all_subdepencies() -> None:
  for path in [
    FILE_CORE,
    FILE_CORE_DEP,
    FILE_DEV,
    FILE_DEV_DEP,
    FILE_BUILD,
    FILE_BUILD_DEP,
  ]:
    update_requirement_txt(path)


if __name__ == '__main__':
  colorama.init(autoreset=True)
  update_all_subdepencies()
