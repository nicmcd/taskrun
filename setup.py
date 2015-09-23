import codecs
import re
import os
import sys

try:
  from setuptools import setup
except:
  print('please install setuptools via pip:')
  print('  pip3 install setuptools')
  sys.exit(-1)

def find_version(*file_paths):
    version_file = codecs.open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), *file_paths), 'r').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='taskrun',
    version=find_version('taskrun', '__init__.py'),
    description='Parallel task management with dependencies',
    author='Nic McDonald',
    author_email='nicci02@hotmail.com',
    license='BSD',
    url='http://github.com/nicmcd/taskrun',
    packages=['taskrun'],
    install_requires=['termcolor >= 1.1.0'],
    )
