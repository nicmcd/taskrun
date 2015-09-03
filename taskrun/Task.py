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
This defines one task to be executed
Each task has a set of dependencies, which are other tasks
Each task notifies all tasks that are dependent on it upon completion
"""
class Task(threading.Thread):

  """
  This instantiates a Task object, which is "abstract"
  """
  def __init__(self, manager, name, **kwargs):
    threading.Thread.__init__(self)
    self._manager = manager
    self._manager.add_task(self)
    self._name = name
    self._dependencies = []
    self._notifiees = []
    self._resources = {}
    for key in kwargs:
      if key.find('res_') == 0:
        self._resources[key[4:]] = kwargs[key]
      else:
        raise TypeError('unsupported kwarg: {0}'.format(key))

  def get_name(self):
    return self._name

  def get_resource(self, resource):
    if resource in self._resources:
      return self._resources[resource]
    else:
      return None

  def add_dependency(self, task):
    if self is task:
      raise ValueError('self dependency is not allowed')
    self._dependencies.append(task)
    task.__add_notifiee(self)

  def __add_notifiee(self, notifiee):
    self._notifiees.append(notifiee)

  def ready(self):
    return not self._dependencies # test for empty

  def task_completed(self, task):
    self._dependencies.remove(task)
    if not self._dependencies: # test for empty
      self._manager.task_is_ready(self)

  def run(self):
    # execute the task
    errors = None
    try:
      errors = self.execute()
    except Exception as ex:
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
    # returns a string representation of this class (not the name)
    raise NotImplementedError("subclasses should override this!")

  def execute(self):
    # returns True for success, False otherwise
    raise NotImplementedError("subclasses should override this!")
