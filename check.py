#!/usr/bin/env python3

import glob
import subprocess

# test cases
for test in glob.glob('test/*'):
  print('')
  print('####################################################################')
  print('testing {0}'.format(test))
  subprocess.check_call('{0}'.format(test), shell=True)

# done
print('\nSUCCESS: everything looks good')
