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
import resource
import psutil
from .process_task import ProcessTask
from .counter_resource import CounterResource

class MemoryResource(CounterResource):
  """
  This class implements a memory resource. This implementation enforces the
  memory usage by using the Python3 resource.RLIMIT_AS
  """

  def _task_used(self, task, uses):
    """
    see CounterResource._task_used()
    """
    # if this is a ProcessTask, enforce memory limit
    if isinstance(task, ProcessTask):
      assert uses > 0.0, 'ProcessTasks must use some memory!'
      # TODO(nicmcd): use the following when Python subprocess is fixed
      #membytes = int(uses * 1024 * 1024 * 1024)
      #task.add_prefunc(lambda: (limit_mem(membytes)))
      memkbytes = int(uses * 1024 * 1024)
      task.command = 'ulimit -v {} && {}'.format(memkbytes, task.command)

  def current_available_memory_gib():
    """
    Returns the currently available memory in the system defined as amount of
    unused memory plus currently cached memory.

    Returns:
      (float) : amount of available memory in GiB
    """
    return psutil.virtual_memory().available / (1024 * 1024 * 1024)

def limit_mem(membytes):
  """
  This uses resource.RLIMIT_AS to limit the amount of address space THIS process
  is able to use. This is intented to be used as a preexec_fn in the
  subprocess.Popen constructor of taskrun.process_task

  Args:
    membytes (int) : the number of bytes to be the threshold
  """
  limits = resource.getrlimit(resource.RLIMIT_AS)
  limits = (membytes, limits[1])
  resource.setrlimit(resource.RLIMIT_AS, limits)
