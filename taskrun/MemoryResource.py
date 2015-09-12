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
from .ProcessTask import ProcessTask
from .Resource import Resource


class MemoryResource(Resource):
  """
  This class implements a memory resource. This implementation enforces the
  memory usage by using the Linux ulimit command.
  """

  def __init__(self, name, default, total):
    """
    Constructs a CounterResource object

    Args:
      name (str)    : the name of the resource
      default (num) : default value of tasks that don't specify it (in GiB)
      total (num)   : total available to be used by tasks (in GiB)
    """
    super(MemoryResource, self).__init__(name, default)
    self._total = total
    self._amount = total

  def can_use(self, task):
    """
    See Resource.can_use()
    """
    uses = task.resource(self.name)
    if uses is None:
      uses = self.default

    if uses > self._total:
      raise ValueError('task \'{0}\' uses {1} units of resource \'{2}\''
                       ' but there is only {3} units total'
                       .format(task.name, uses, self.name,
                               self._total))
    return uses <= self._amount

  def use(self, task):
    """
    See Resource.use()
    """
    uses = task.resource(self.name)
    if uses is None:
      uses = self.default

    if uses > self._total:
      raise ValueError('task \'{0}\' uses {1} units of resource \'{2}\''
                       ' but there is only {3} units total'
                       .format(task.name, uses, self.name,
                               self._total))
    if uses <= self._amount:
      self._amount -= uses

      # if this is a ProcessTask, use ulimit to enforce memory usage
      if isinstance(task, ProcessTask):
        kilobytes = int(uses * 1024 * 1024)
        task.command = 'ulimit -v {0}; {1}'.format(kilobytes, task.command)
      return True
    else:
      return False

  def release(self, task):
    """
    See Resource.release()
    """
    uses = task.resource(self.name)
    if uses is None:
      uses = self.default
    self._amount += uses
    assert self._amount <= self._total
