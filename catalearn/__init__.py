import sys
import warnings
from .upgrade import isLatestVersion

sys.setrecursionlimit(50000)
warnings.filterwarnings('ignore')

if not isLatestVersion():
    print('This version of catalearn is no longer compatible with the backend')
    print('Please use \'pip3 install -U catalearn\' to upgrade to the latest version')
    sys.exit()

from .catalearn import *





