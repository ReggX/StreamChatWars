# native imports
import sys
from pathlib import Path


p = Path(__file__).parent / 'lib'
sys.path.append(str(p.absolute()))
