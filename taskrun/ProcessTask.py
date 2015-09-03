"""
Copyright (c) 2013-2015, Nic McDonald
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import multiprocessing
import os
import subprocess
import threading
import time
import sys

from .Task import Task


"""
This class is a Task that runs as a subprocess
"""
class ProcessTask(Task):

  """
  This instiates a ProcessTask object with a subprocess command
  """
  def __init__(self, manager, name, command, stdout=None, stderr=None):
    super(ProcessTask, self).__init__(manager, name)
    self._command = command
    self._stdout_file = stdout
    self._stderr_file = stderr

  def describe(self):
    text = self._command
    if self._stdout_file:
      text += " 1> " + self._stdout_file
    if self._stderr_file:
      text += " 2> " + self._stderr_file
    return text

  def execute(self):
    # format stdout and stderr outputs
    if self._stdout_file:
      stdout_fd = open(self._stdout_file, 'w')
    else:
      stdout_fd = subprocess.PIPE
    if self._stderr_file:
      stderr_fd = open(self._stderr_file, 'w')
    else:
      stderr_fd = subprocess.PIPE

    # execute the task command
    proc = subprocess.Popen(self._command, stdout=stdout_fd, stderr=stderr_fd,
                            shell=True)

    # wait for the process to finish, collect output
    self.stdout, self.stderr = proc.communicate()
    if self.stdout is not None:
      self.stdout = self.stdout.decode('utf-8')
    if self.stderr is not None:
      self.stderr = self.stderr.decode('utf-8')

    # close the output files
    if self._stdout_file:
      stdout_fd.close()
    if self._stderr_file:
      stderr_fd.close()

    # check the return code
    ret = proc.returncode
    if ret == 0:
      return None
    else:
      return ret
