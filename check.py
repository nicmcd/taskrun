#!/usr/bin/env python3

import glob
import subprocess

# lint
print('linting')
subprocess.check_call('pylint --rcfile=pylintrc -r n taskrun', shell=True)

# test cases
for test in glob.glob('test/*'):
  print('testing {0}'.format(test))
  subprocess.check_call('{0}'.format(test), shell=True)

# done
print('\nSUCCESS: everything looks good')
