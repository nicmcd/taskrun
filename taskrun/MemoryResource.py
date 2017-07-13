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
import math
import resource
import psutil
from .ProcessTask import ProcessTask
from .Resource import Resource


class MemoryResource(Resource):
  """
  This class implements a memory resource. This implementation enforces the
  memory usage by using the Python3 resource.RLIMIT_AS
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

      # if this is a ProcessTask, enforce memory limit
      if isinstance(task, ProcessTask):
        membytes = int(uses * 1024 * 1024 * 1024)
        task.add_prefunc(lambda: (limit_mem(membytes)))
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

  def current_available_memory_gib():
    """
    Returns the currently available memory in the system defined as amount of
    unused memory plus currently cached memory.

    Returns:
      (float) : amount of available memory in GiB
    """
    return math.floor((psutil.virtual_memory().available) /
                      (1024 * 1024 * 1024))


def limit_mem(membytes):
  """
  This uses resource.RLIMIT_AS to limit the amount of address space THIS process
  is able to use. This is intented to be used as a preexec_fn in the
  subprocess.Popen constructor of taskrun.ProcessTask

  Args:
    membytes (int) : the number of bytes to be the threshold
  """
  limits = resource.getrlimit(resource.RLIMIT_AS)
  limits = (membytes, limits[1])
  resource.setrlimit(resource.RLIMIT_AS, limits)
