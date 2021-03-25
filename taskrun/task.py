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
import threading


class Task(threading.Thread):
  """
  This defines one task to be executed
  Each task has a set of dependencies, which are other tasks
  Each task notifies all tasks that are dependent on it upon completion
  """

  def __init__(self, manager, name):
    """
    This instantiates a Task object, which is "abstract"

    Args:
      manager (TaskManager) : the task manager this should be associated with
      name (string)         : the name of this task
    """

    threading.Thread.__init__(self, name=name)
    self._manager = manager
    self._manager.add_task(self)
    self._resources = {}
    self._priority = 0
    self._dependencies = []
    self._dependents = []
    self.conditions = []
    self._bypass = None
    self._errors = None
    self.killed = False

  @property
  def priority(self):
    """
    Returns:
      (num) : the priority of this task
    """
    return self._priority

  @priority.setter
  def priority(self, value):
    """
    Sets the priority of this task

    Args:
      value (comparable) : the new priority
    """
    assert isinstance(value, int) and value >= 0, \
      'priority must be an int >= 0, {} is not'.format(value)
    self._priority = value

  @property
  def resources(self):
    """
    Returns:
      (dict<str,num>) : the resources needed by this task
    """
    return self._resources

  @resources.setter
  def resources(self, value):
    """
    Sets the resources needed by this task

    Args:
      value (dict<str,num>) : resources
    """
    self._resources = value

  def resource(self, resource):
    """
    Returns the quantity of a given resource

    Args:
      resource (str) : resource to be queried
    """

    if resource in self._resources:
      return self._resources[resource]
    return None

  def get_dependencies(self):
    """
    Returns:
      (list) : the list of dependencies
    """
    return self._dependencies

  def add_dependency(self, task):
    """
    Adds a dependency task to this task

    Args:
      task (Task) : a task dependency
    """

    # perform a cyclic dependency check (BFS checking for self)
    visit = [task]
    visited = set()
    while len(visit) > 0:
      curr = visit.pop()
      if curr is self:
        raise ValueError('cyclic dependency found')
      visited.add(curr)
      for dep in curr._dependencies:  #pylint: disable=protected-access
        if dep not in visited:
          visit.append(dep)

    # add the task as a dependency
    assert task not in self._dependencies
    self._dependencies.append(task)

    # add self to the task's dependent list
    task.add_dependent(self)

  def get_dependents(self):
    """
    Returns:
      (list) : the list of dependents
    """
    return self._dependents

  def add_dependent(self, dependent):
    """
    Adds a dependent to the list

    Args:
      dependent (Task) : a task to be notified when this one completes
    """
    self._dependents.append(dependent)

  def ready(self):
    """
    Returns:
      (bool) : tests whether this task is ready to execute
    """
    return not self._dependencies # test for empty

  def add_condition(self, condition):
    """
    Adds a condition to this task. Each condition is evaluated after all
    dependencies have been met.

    Args:
      condition (Condition) : a condition for this task
    """
    assert self._bypass is None
    self.conditions.append(condition)


  def task_done(self, task):
    """
    Notification that a dependency is now done

    Args:
      task (Task) : the task that is now done
    """

    self._dependencies.remove(task)
    if len(self._dependencies) == 0:
      self._manager.task_ready(self)

  @property
  def bypass(self):
    """
    Returns:
      (bool) : True if the process should be bypassed (not executed),
               False if it should execute
    """

    if self._bypass is None:
      if len(self.conditions) == 0:
        # always run if no conditions
        self._bypass = False
      else:
        # default to bypassing unless at least one condition says to run
        self._bypass = True
        for condition in self.conditions:
          if condition.check():
            self._bypass = False
          break
    return self._bypass

  def run(self):
    """
    This either executes the task or performs the bypass.
    """

    # execute the task
    assert self._bypass is not None, "bypass was never set"
    if not self._bypass:
      # try to execute
      try:
        self._errors = self.execute()
      except Exception as ex:  # pylint: disable=broad-except
        self._errors = ex

      # report to the task manager
      if self.killed:
        self._manager.task_killed(self)
      elif self._errors is None:
        self._manager.task_completed(self)
      else:
        self._manager.task_failed(self, self._errors)

    # inform all dependents of task completion/bypass
    for dependent in self._dependents:
      dependent.task_done(self)

  def describe(self):
    """
    Returns:
      (str) : a description of this task (not the name)
    """
    raise NotImplementedError('subclasses should override this!')

  def execute(self):
    """
    Executes this task.

    WARNING: subclass implementations

    Returns:
      (None or errors) : None for success, errors on failure,
    """
    raise NotImplementedError('subclasses should override this!')

  def kill(self):
    """
    Kills this task. This may or may not be possible, but when it is, it must be
    immediately carryied out.

    WARNING: subclass implementations must set self.killed = True if the process
    was actually killed.
    """
    raise NotImplementedError('subclasses should override this!')
