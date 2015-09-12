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
import subprocess

from .Task import Task



class ProcessTask(Task):
  """
  This class is a Task that runs as a subprocess
  """

  def __init__(self, manager, name, command=None):
    """
    This instiates a ProcessTask object with a subprocess command

    Args:
      manager (TaskManager) : passed to Task.__init__()
      name (str)            : passed to Task.__init__()
      command (str)         : the command to be run
    """

    super(ProcessTask, self).__init__(manager, name)
    self._command = command
    self._stdout_file = None
    self._stderr_file = None
    self.stdout = None
    self.stderr = None
    self._proc = None

  @property
  def command(self):
    """
    Returns:
      (str) : the process's command
    """
    return self._command

  @command.setter
  def command(self, value):
    """
    Sets the process's command

    Args:
      value (str) : the new command
    """
    self._command = value

  @property
  def stdout_file(self):
    """
    Returns:
      (str) : filename for stdout text
    """
    return self._stdout_file

  @stdout_file.setter
  def stdout_file(self, filename):
    """
    Sets the filename of the stdout text

    Args:
      filename (str) : a filename for stdout text
    """
    self._stdout_file = filename

  @property
  def stderr_file(self):
    """
    Returns:
      (str) : filename for stderr text
    """
    return self._stderr_file

  @stderr_file.setter
  def stderr_file(self, filename):
    """
    Sets the filename of the stderr text

    Args:
      filename (str) : a filename for stderr text
    """
    self._stderr_file = filename

  def describe(self):
    """
    See Task.describe()
    """

    text = self._command
    if self._stdout_file:
      text += " 1> " + self._stdout_file
    if self._stderr_file:
      text += " 2> " + self._stderr_file
    return text

  def execute(self):
    """
    See Task.execute()
    """

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
    self._proc = subprocess.Popen(self._command, stdout=stdout_fd,
                                  stderr=stderr_fd, shell=True)

    # wait for the process to finish, collect output
    self.stdout, self.stderr = self._proc.communicate()
    if self.stdout is not None:
      self.stdout = self.stdout.decode('utf-8')
    if self.stderr is not None:
      self.stderr = self.stderr.decode('utf-8')

    # close the output files
    if self._stdout_file:
      #pylint: disable=maybe-no-member
      stdout_fd.close()
    if self._stderr_file:
      #pylint: disable=maybe-no-member
      stderr_fd.close()

    # check the return code
    ret = self._proc.returncode
    if ret == 0:
      return None
    else:
      return ret

  def kill(self):
    """
    See Task.kill()
    This implementation calls subprocess.kill()
    """

    self.killed = True

    # there is a chance the proc hasn't been created yet or has already
    #  completed
    if self._proc:
      self._proc.kill()
