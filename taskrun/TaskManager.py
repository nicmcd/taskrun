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
    self._access_lock = threading.Lock()

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
    self._access_lock.acquire()
    self._ready_tasks.append(task)
    self._access_lock.release()

  """
  This is called by a Task when it has completed execution
  """
  def task_completed(self, task):
    self._access_lock.acquire()
    self._tasks.remove(task)
    self._running_tasks.remove(task)
    self._access_lock.release()

    # inform the resource manager of the completion
    self._resource_manager.task_completed(task)

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

    # set task settings
    for task in self._tasks:
      # ask the tasks to report if they are ready to run
      # (find root tasks)
      if task.ready():
        self.task_is_ready(task)

    # run all tasks until there is none left
    while True:
      # get the number of tasks left
      self._access_lock.acquire()
      num_tasks_left = len(self._tasks)
      num_ready_tasks = len(self._ready_tasks)
      self._access_lock.release()

      # check if done
      if num_tasks_left == 0:
        break;

      # wait for an available task to run
      if num_ready_tasks == 0:
        time.sleep(0.25)  # 250ms
        continue

      # get the next ready task
      self._access_lock.acquire()
      task = self._ready_tasks[0]
      self._ready_tasks.remove(task)
      self._access_lock.release()

      # wait until the task can run
      while self._resource_manager.task_starting(task) == False:
        time.sleep(0.25)  # 250ms

      # append task to running tasks list
      self._access_lock.acquire()
      self._running_tasks.append(task)
      self._access_lock.release()

      # notify observer
      if 'task_starting' in dir(self._observer):
        self._observer.task_starting(task)

      # run it
      task.start()

    # turn off
    self._running = False
