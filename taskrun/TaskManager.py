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
from .FailureMode import FailureMode
import threading
import time


class TaskManager(object):
  """
  This class manages a group of tasks
  """

  def __init__(self, resource_manager=None, observer=None,
               failure_mode=FailureMode.AGGRESSIVE_FAIL):
    """
    Constructs a TaskManager object

    Args:
      resource_manager (ResourceManager) : the resource manager to use
      observer (Observer)                : the observer to user
    """

    self._running = False
    self._waiting_tasks = []
    self._ready_tasks = []
    self._running_tasks = []
    self._filter_tasks = []
    self._resource_manager = resource_manager
    self._observer = observer
    self._condition_variable = threading.Condition()
    self._failure_mode = FailureMode.create(failure_mode)

  def add_task(self, task):
    """
    This adds a task to this manager

    Args:
      task (Task) : the task to add
    """

    assert self._running == False
    self._waiting_tasks.append(task)

  def _probe_ready(self):
    """
    This method probes the waiting tasks to see if they are ready
    """
    assert self._running == True
    temp_ready = []
    for task in self._waiting_tasks:
      if task.ready():
        temp_ready.append(task)
    for task in temp_ready:
      self.task_ready(task)

  def task_ready(self, task):
    """
    This is called by a Task when it becomes ready to run

    Args:
      task (Task) : the task that is now ready to run
    """

    assert self._running == True
    with self._condition_variable:
      # check if this task is in the filter list
      if task in self._filter_tasks:
        assert task not in self._waiting_tasks
        self._filter_tasks.remove(task)

      else:
        # transfer from waiting to ready list
        self._waiting_tasks.remove(task)
        self._ready_tasks.append(task)

      # notify waiting threads
      self._condition_variable.notify()

  def _task_started(self, task):
    """
    This is called when a Task has started execution

    WARNING: this method must be called while locked on the condition variable

    Args:
      task (Task) : the task that completed
    """
    assert self._running == True

    # notify observer
    if self._observer is not None:
      self._observer.task_started(task)

  def _task_bypassed(self, task):
    """
    This is called when a Task has been bypassed

    WARNING: this method must be called while locked on the condition variable

    Args:
      task (Task) : the task that bypassed
    """
    assert self._running == True

    # notify observer
    if self._observer is not None:
      self._observer.task_bypassed(task)

    # clean up the task
    self._task_done(task)

  def task_completed(self, task):
    """
    This is called when a Task has completed execution

    Args:
      task (Task) : the task that completed
    """
    assert self._running == True

    with self._condition_variable:
      # pass info to the observer
      if self._observer is not None:
        self._observer.task_completed(task)

      # clean up the task
      self._task_done(task)

  def task_failed(self, task, errors):
    """
    This function is called by a task when an error code is returned from
    the task

    Args:
      task (Task) : the task that encountered errors
    """
    assert self._running == True

    # handle the failure
    with self._condition_variable:
      # handle failure based on failure mode
      if self._failure_mode is FailureMode.AGGRESSIVE_FAIL:
        # kill all the currently running tasks
        if not task.killed:
          for running_task in self._running_tasks:
            if running_task is not task:
              running_task.kill()

        # clear out waiting and ready lists
        self._filter_tasks.extend(self._waiting_tasks)
        self._waiting_tasks = []
        self._filter_tasks.extend(self._ready_tasks)
        self._ready_tasks = []

      elif self._failure_mode is FailureMode.PASSIVE_FAIL:
        # clear out waiting and ready lists
        self._filter_tasks.extend(self._waiting_tasks)
        self._waiting_tasks = []
        self._filter_tasks.extend(self._ready_tasks)
        self._ready_tasks = []

      elif self._failure_mode is FailureMode.ACTIVE_CONTINUE:
        # remove all tasks that depend on this task (BFS)
        visit = []
        visit.extend(task.get_dependents())
        visited = set()
        while len(visit) > 0:
          curr = visit.pop()
          assert curr not in self._ready_tasks
          assert curr not in self._running_tasks
          visited.add(curr)
          for dep in curr.get_dependents():
            if dep not in visited:
              visit.append(dep)
          if curr in self._waiting_tasks:
            self._waiting_tasks.remove(curr)
            self._filter_tasks.append(curr)

      elif self._failure_mode is FailureMode.BLIND_CONTINUE:
        # do nothing
        pass

      else:
        assert False, "programmer error, fire somebody!"

      # pass info to the observer
      if self._observer is not None:
        self._observer.task_failed(task, errors)

      # clean up the task
      self._task_done(task)

  def _task_done(self, task):
    """
    This method is called by task_completed and task_failed.
    This method removes the task from the running list and gives back all
    resources it consumed.

    WARNING: this method must be called while locked on the condition variable

    Args:
      task (Task) : the task that finished
    """
    assert self._running == True

    # remove task from running lists
    self._running_tasks.remove(task)

    # give back resources
    if not task.bypass():
      if self._resource_manager is not None:
        self._resource_manager.done(task)

    # notify waiting thread
    self._condition_variable.notify()

  def run_tasks(self):
    """
    This runs all tasks in dependency order and executing with the
    ResourceManager's discretion
    """
    assert self._running == False
    self._running = True

    # ask the tasks if they are ready to run (find root tasks)
    self._probe_ready()

    # run all tasks until there is none left
    while True:
      # use the condition variable for pausing/resuming and locking
      with self._condition_variable:
        # check if we are done
        if (len(self._waiting_tasks) == 0 and
            len(self._ready_tasks) == 0 and
            len(self._running_tasks) == 0): # and
            #len(self._filter_tasks) == 0):
          break

        # wait for a ready task
        if len(self._ready_tasks) == 0:
          self._condition_variable.wait()
          continue

        # find the highest priority task in FIFO order
        next_task = self._ready_tasks[0]
        for task in self._ready_tasks[1:]:
          if (next_task.priority is None and
              task.priority is not None):
            next_task = task
          elif (next_task.priority is not None and
                task.priority is not None and
                task.priority > next_task.priority):
            next_task = task

        # check for task bypassing
        bypass = next_task.bypass()

        # if not being bypassed, check if there enough resources to run the task
        #  on success, the resource will have been used
        if (not bypass and
            self._resource_manager is not None and
            self._resource_manager.start(next_task) == False):
          self._condition_variable.wait()
          continue

        # transfer from ready to running
        self._ready_tasks.remove(next_task)
        self._running_tasks.append(next_task)

        # signal started or bypassed
        if not bypass:
          self._task_started(next_task)
        else:
          self._task_bypassed(next_task)

      # at this point, the next_task is either being bypassed or there is enough
      #  resources to execute the task

      # run it
      next_task.start()

      # give up execution to other threads/processes
      #  this allows tasks to start
      time.sleep(0.000001)

    # turn off
    self._running = False
