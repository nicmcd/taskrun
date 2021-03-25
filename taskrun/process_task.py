"""
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
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
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
import os
import signal
import subprocess
import threading
from .task import Task


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
    super().__init__(manager, name)
    self._command = command
    self._stdout_file = None
    self._stderr_file = None
    self.stdout = None
    self.stderr = None
    self.returncode = None
    self._proc = None
    self._prefuncs = []
    self._lock = threading.Lock()

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

  def add_prefunc(self, func):
    """
    Adds a function (any callable) to be executed after the fork before the exec

    Args:
      func (callable) : a callable to be executed
    """
    # TODO(nicmcd): when will preexec_fn be supported?
    raise NotImplementedError('ProcessTask does not yet support pre-execution '
                              'functions due to Python subprocess limitations.')
    #self._prefuncs.append(func)

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

    with self._lock:
      # If we're killed at this point, don't bother starting a new process.
      if self.killed:
        print('already killed {}'.format(self.name))
        return None

      # format stdout and stderr outputs
      if self._stdout_file:
        stdout_fd = open(self._stdout_file, 'w')
      else:
        stdout_fd = subprocess.PIPE
      if self._stderr_file:
        if self._stderr_file.lower() == 'stdout':
          stderr_fd = subprocess.STDOUT
        elif self._stderr_file == self._stdout_file:
          stderr_fd = stdout_fd
        else:
          stderr_fd = open(self._stderr_file, 'w')
      else:
        stderr_fd = subprocess.PIPE

      # executes the task command
      self._proc = subprocess.Popen(
        self._command, stdout=stdout_fd, stderr=stderr_fd, shell=True,
        start_new_session=True)

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
    if self._stderr_file and not self._stderr_file.lower() == 'stdout':
      #pylint: disable=maybe-no-member
      stderr_fd.close()

    # get the return code
    #with self._lock:
    self.returncode = self._proc.returncode

    # check the return code
    if self.returncode == 0:
      return None
    return self.returncode

  def kill(self):
    """
    See Task.kill()
    This implementation calls Popen.terminate()
    """

    with self._lock:
      # Don't kill if already completed or already killed
      if self.returncode is None and not self.killed:
        self.killed = True
        # there is a chance the proc hasn't been created yet
        if self._proc is not None:
          try:
            # self._proc.terminate() doesn't work likely because the process is
            # a shell process and the SIGTERM isn't being properly propagated.
            # Killing the whole process group seems to work.
            os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
          except ProcessLookupError:
            pass
