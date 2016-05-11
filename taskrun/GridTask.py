"""
 * Copyright (c) 2012-2016, Nic McDonald
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""
# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import subprocess

from .Task import Task

class GridTask(Task):
  """
  This class is a Task that runs as a grid process. See
  http://gridscheduler.sourceforge.net/
  """

  def __init__(self, manager, name, command):
    """
    This instiates a Gridobject with a subprocess command

    Args:
      manager (TaskManager) : passed to Task.__init__()
      name (str)            : passed to Task.__init__()
      command (str)         : the command to be run
    """

    super(GridTask, self).__init__(manager, name)
    self._command = command
    self._stdout_file = '/dev/null'
    self._stderr_file = '/dev/null'

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
    Sets the filename of the stderr text.

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
    # execute the task command and wait for it to finish
    ret = subprocess.call([
      'qsub',
      '-sync', 'yes',           # wait for job to complete before exiting
      '-N', self.name,          # name of the task
      '-o', self._stderr_file,  # stdout
      '-e', self._stderr_file,  # stderr
      '-b', 'yes',              # execute binary file instead of job script
      '-cwd',                   # use current working directory
      self._command])

    # check the return code
    if ret == 0:
      return None
    else:
      return ret

  def kill(self):
    """
    See Task.kill()
    """

    self.killed = True
