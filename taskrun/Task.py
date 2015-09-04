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
import threading


#pylint: disable=abstract-class-not-used
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
    self._priority = None
    self._dependencies = []
    self._notifiees = []

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
    else:
      return None

  def add_dependency(self, task):
    """
    Adds a dependency task to this task

    Args:
      task (Task) : a task dependency
    """

    if self is task:
      raise ValueError('self dependency is not allowed')
    self._dependencies.append(task)
    task.add_notifiee(self)

  def add_notifiee(self, notifiee):
    """
    Adds a notifiee to the list

    Args:
      notifiee (Task) : a task to be notified when this one completes
    """
    self._notifiees.append(notifiee)

  def ready(self):
    """
    Returns:
      (bool) : tests whether this task is ready to execute
    """
    return not self._dependencies # test for empty

  def task_completed(self, task):
    """
    Notification that a dependency has completed

    Args:
      task (Task) : the task that completed
    """

    self._dependencies.remove(task)
    if not self._dependencies: # test for empty
      self._manager.task_ready(self)

  def run(self):
    """
    Executes the task by calling its execute() function
    """

    # execute the task
    errors = None
    try:
      errors = self.execute()
    except RuntimeError as ex:
      errors = ex

    # handle potential errors
    if errors is not None:
      self._manager.task_error(self, errors)  # aborts programs

    # inform the manager of task completion
    self._manager.task_completed(self)
    # inform all notifiees of task completion
    for notifiee in self._notifiees:
      notifiee.task_completed(self)

  def describe(self):
    """
    Returns:
      (str) : a description of this task (not the name)
    """
    raise NotImplementedError("subclasses should override this!")

  def execute(self):
    """
    Executes this task

    Returns:
      (None or errors) : None for success, errors on failure
    """
    raise NotImplementedError("subclasses should override this!")
