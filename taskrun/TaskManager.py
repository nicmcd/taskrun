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
import multiprocessing
import os
import subprocess
import threading
import time
import sys


"""
This class manages a group of tasks
"""
class TaskManager(object):

  def __init__(self, resource_manager, observer):
    self._running = False
    self._tasks = []
    self._ready_tasks = []
    self._running_tasks = []
    self._resource_manager = resource_manager
    self._observer = observer
    self._condition_variable = threading.Condition()

  """
  This adds a task to this manager
  """
  def add_task(self, task):
    assert self._running == False
    self._tasks.append(task)

  """
  Retrieves the number of tasks
  """
  def num_tasks(self):
    return len(self._tasks)

  """
  This is called by a Task when it becomes ready to run
  """
  def task_is_ready(self, task):
    with self._condition_variable:
      # add task to ready list
      self._ready_tasks.append(task)

      # notify waiting threads
      self._condition_variable.notify()

  """
  This is called by a Task when it has completed execution
  """
  def task_completed(self, task):
    with self._condition_variable:
      # remove task from lists
      self._tasks.remove(task)
      self._running_tasks.remove(task)

      # give back resources
      self._resource_manager.task_completed(task)

      # notify waiting threads
      self._condition_variable.notify()

    # pass info to the observer
    if 'task_completed' in dir(self._observer):
      self._observer.task_completed(task)

  """
  This function is called by a task when an error code is returned from
  the task
  """
  def task_error(self, task, errors):
    # pass info to the observer
    if 'task_error' in dir(self._observer):
      self._observer.task_error(task, errors)

    # kill
    os._exit(-1)

  """
  This runs all tasks in dependency order and executing with the
  ResourceManager's discretion
  """
  def run_tasks(self):
    assert self._running == False
    self._running = True

    # ignore empty call
    if not self._tasks: # not empty check
      return

    # ask the tasks if they are ready to run (find root tasks)
    for task in self._tasks:
      if task.ready():
        self._ready_tasks.append(task)

    # run all tasks until there is none left
    while True:
      next_task = None

      # use the condition variable for pausing/resuming
      with self._condition_variable:
        # check if we are done
        if len(self._tasks) == 0:
          break;

        # wait for at least one ready task
        if len(self._ready_tasks) == 0:
          self._condition_variable.wait()
          continue

        # find the highest priority task
        next_task = self._ready_tasks[0]
        for task in self._ready_tasks[1:]:
          if (next_task.priority is None and
              task.priority is not None):
            next_task = task
          elif (next_task.priority is not None and
                task.priority is not None and
                task.priority > next_task.priority):
            next_task = task

        # check if there enough resources to run the task
        if self._resource_manager.task_starting(next_task) == False:
          self._condition_variable.wait()
          continue

        # set to running (remove from ready, add to running)
        self._ready_tasks.remove(next_task)
        self._running_tasks.append(next_task)

      # this indent escapes the condition variable lock
      #  now run the next task

      # notify observer
      if 'task_starting' in dir(self._observer):
        self._observer.task_starting(next_task)

      # run it
      next_task.start()

      # give up execution to other threads/processes
      #  this allows tasks to start
      time.sleep(0.000001)

    # turn off
    self._running = False
