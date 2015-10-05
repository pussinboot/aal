from aal import aal
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
aal.main(sys.argv[1:])