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
from .process_task import ProcessTask
from .resource import Resource


class CpuTimeResource(Resource):
  """
  This class implements a CPU time resource. This implementation enforces the
  memory usage by using the Python3 resource.RLIMIT_CPU
  """

  def __init__(self, name, default):
    """
    Constructs a CounterResource object

    Args:
      name (str)    : the name of the resource
      default (num) : default value of tasks that don't specify it (in secs)
    """
    super().__init__(name, default)
    assert isinstance(default, int), '"default" must be an int'

  def can_use(self, task):
    """
    See Resource.can_use()
    """
    if task.resource(self.name) is not None:
      assert isinstance(task, ProcessTask), ('only ProcessTasks can use '
                                             'CpuTimeResources')
    return True

  def use(self, task):
    """
    See Resource.use()
    """
    secs = task.resource(self.name)
    if secs is None:
      secs = self.default
    else:
      assert isinstance(task, ProcessTask), ('only ProcessTasks can use '
                                             'CpuTimeResources')
      assert isinstance(secs, int), '"{0}" must be an int'.format(self.name)

    # enforce CPU time limit on the ProcessTask
    if isinstance(task, ProcessTask):
      assert int(secs) > 0
      # TODO(nicmcd): use the following when Python subprocess is fixed
      #task.add_prefunc(lambda: (limit_cputime(secs)))
      task.command = 'ulimit -t {} && {}'.format(int(secs), task.command)

    return True

  def release(self, task):
    """
    See Resource.release()
    """


def limit_cputime(secs):
  """
  This uses resource.RLIMIT_CPU to limit the amount of CPU time THIS process
  is able to use. This is intented to be used as a preexec_fn in the
  subprocess.Popen constructor of taskrun.process_task

  Args:
    membytes (int) : the number of bytes to be the threshold
  """
  limits = resource.getrlimit(resource.RLIMIT_CPU)
  limits = (secs, limits[1])
  resource.setrlimit(resource.RLIMIT_CPU, limits)
