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
from .resource import Resource

class CounterResource(Resource):
  """
  This class implements a counter as a resource
  """

  def __init__(self, name, default, total):
    """
    Constructs a CounterResource object

    Args:
      name (str)    : the name of the resource
      default (num) : default value of tasks that don't specify it
      total (num)   : total available to be used by tasks
    """
    super().__init__(name, default)
    self._total = total
    self._amount = total
    self._tolerance = float(self._total) / 1e6

  @property
  def total(self):
    """
    Returns the total count
    """
    return self._total

  @property
  def used(self):
    """
    Returns the used count
    """
    return self._total - self._amount

  def can_use(self, task):
    """
    See Resource.can_use()
    """
    uses = task.resource(self.name)
    if uses is None:
      uses = self.default

    if (uses - self._total) > self._tolerance:
      raise ValueError('task \'{0}\' uses {1} units of resource \'{2}\''
                       ' but there is only {3} units total'
                       .format(task.name, uses, self.name,
                               self._total))
    return (self._amount - uses) > -self._tolerance

  def use(self, task):
    """
    See Resource.use()
    """
    uses = task.resource(self.name)
    if uses is None:
      uses = self.default

    if (uses - self._total) > self._tolerance:
      raise ValueError('task \'{0}\' uses {1} units of resource \'{2}\''
                       ' but there is only {3} units total'
                       .format(task.name, uses, self.name,
                               self._total))
    if (self._amount - uses) > -self._tolerance:
      # use and saturate at zero within tolerance
      self._amount -= uses
      if self._amount < 0.0:
        assert abs(self._amount) < self._tolerance
        self._amount = 0.0

      # perform _task_used specialization
      self._task_used(task, uses)
      return True
    return False

  def release(self, task):
    """
    See Resource.release()
    """
    uses = task.resource(self.name)
    if uses is None:
      uses = self.default
    self._amount += uses

    # Repeated floating point rounding errors might make amount be greater than
    #  total. Use a near compare, then saturate at total.
    if self._amount > self._total:
      assert abs(self._amount - self._total) < self._tolerance
      self._amount = self._total

    # perform _task_released specialization
    self._task_released(task, uses)

  def _task_used(self, task, uses):
    """
    This is a function that subclasses can override for specialization.
    This gets called just after the task used the resource.
    """

  def _task_released(self, task, uses):
    """
    This is a function that subclasses can override for specialization.
    This gets called just after the task released the resource.
    """
