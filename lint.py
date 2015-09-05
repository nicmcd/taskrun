#!/usr/bin/env python3

import subprocess

subprocess.check_call('pylint --rcfile=pylintrc -r n taskrun', shell=True)

# done
print('\nSUCCESS: everything looks good')
