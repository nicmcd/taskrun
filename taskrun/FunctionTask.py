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

# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from .Task import Task


class FunctionTask(Task):
  """
  This class is a Task that runs as a function call
  """

  def __init__(self, manager, name, func, *args, **kwargs):
    """
    This instiates a FunctionTask object with a function and arguments

    Args:
      manager (TaskManager) : passed to Task.__init__()
      name (str)            : passed to Task.__init__()
      func (function)       : the function to be executed
      *args                 : passed to func when executed
      **kwargs              : passed to func when executed
    """

    super(FunctionTask, self).__init__(manager, name)
    self._func = func
    self._args = args
    self._kwargs = kwargs
    self._done = False

  def describe(self):
    """
    See Task.describe()
    """

    return 'def {0}(args={1}, kwargs={2})'.format(
      self._func.__name__, self._args, self._kwargs)

  def execute(self):
    """
    See Task.execute()
    """

    self._done = True
    res = self._func(*self._args, **self._kwargs)
    return res

  def kill(self):
    """
    See Task.kill()
    This implementation ignores this because it can't kill the function
    call once it has already been made.
    """
    if not self._done:
      self.killed = True
