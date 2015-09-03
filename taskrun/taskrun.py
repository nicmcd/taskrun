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


# conditionally import the termcolor package, it's OK if it doesn't exist
try:
  USE_TERM_COLOR = True
  from termcolor import colored
except ImportError:
  USE_TERM_COLOR = False
USE_TERM_COLOR &= sys.stdout.isatty()


"""
This defines one task to be executed
Each task has a set of dependencies, which are other tasks
Each task notifies all tasks that are dependent on it upon completion
"""
class Task(threading.Thread):

  """
  This instiates a Task object, which is "abstract"
  """
  def __init__(self, manager, name):
    threading.Thread.__init__(self)
    self._manager = manager
    self._manager.add_task(self)
    self._name = name
    self._dependencies = []
    self._notifiees = []
    self._runnable = True
    self._accessLock = threading.Lock()

  def get_name(self):
    return self._name

  def add_dependency(self, task):
    if self is task:
      raise ValueError('self dependency is not allowed')
    self._dependencies.append(task)
    task.__add_notifiee(self)

  def __add_notifiee(self, notifiee):
    self._notifiees.append(notifiee)

  def set_runnable(self, run):
    self._run = run

  def ready(self):
    return not self._dependencies # test for empty

  def task_is_done(self, task):
    self._dependencies.remove(task)
    if not self._dependencies: # test for empty
      self._manager.task_is_ready(self)

  def run(self):
    # inform the manager that this task is now running
    self._manager.task_is_running(self)

    # run the task (optionally)
    if self._run:
      # execute the task
      errors = None
      try:
        errors = self.execute()
      except Exception as ex:
        print('Exception caught')
        errors = ex
      if errors is not None:
        self._manager.task_error(self, errors)

    # inform the manager of task completion
    self._manager.task_is_done(self)
    # inform all notifiees of task completion
    for notifiee in self._notifiees:
      notifiee.task_is_done(self)

  def describe(self):
    # returns a string representation of this class (not the name)
    raise NotImplementedError("subclasses should override this!")

  def execute(self):
    # returns True for success, False otherwise
    raise NotImplementedError("subclasses should override this!")


"""
This class is a Task that runs as a subprocess
"""
class ProcessTask(Task):

  """
  This instiates a ProcessTask object with a subprocess command
  """
  def __init__(self, manager, name, command=None, output_file=None):
    super(ProcessTask, self).__init__(manager, name)
    self._command = command
    self._output_file = output_file

  def describe(self):
    text = self._command
    if self._output_file:
      text += " &> " + self._output_file
    return text

  def execute(self):
    # execute the task command
    if self._output_file is not None:
      ofd = open(self._output_file, 'w')
    else:
      ofd = open('/dev/null', 'w')
    proc = subprocess.Popen(self._command, stdout=ofd, stderr=ofd, \
                            shell=True)

    # wait for the process to finish
    proc.communicate()
    # close the output
    ofd.close()
    # check the return code
    ret = proc.returncode
    if ret == 0:
      return None
    else:
      return ret


"""
This class is a Task that runs as a function call
"""
class FunctionTask(Task):

  """
  This instiates a FunctionTask object with a function and arguments
  """
  def __init__(self, manager, name, func, *args, **kwargs):
    super(FunctionTask, self).__init__(manager, name)
    self._func = func
    self._args = args
    self._kwargs = kwargs

  def describe(self):
    return "def {0}(args={1}, kwargs={2})".format(
      self._func.__name__, self._args, self._kwargs)

  def execute(self):
    return self._func(*self._args, **self._kwargs)


"""
This class manages a group of tasks
"""
class Manager(object):

  def __init__(self, numProcs=None, runTasks=True,
               showDescriptions=True, showProgress=True):
    self._numProcs = numProcs
    if not numProcs:
      self._numProcs = multiprocessing.cpu_count()
    self._printLock = threading.Lock()
    self._tasks = []
    self._readyTasks = []
    self._runningTasks = []
    self._printLock = threading.Lock()
    self._showDescriptions = showDescriptions
    self._runTasks = runTasks
    self._showProgress = showProgress
    self._totalTasks = None

  """
  This adds a task to this manager
  """
  def add_task(self, task):
    self._tasks.append(task)

  """
  This is called by a Task when it becomes ready to run
  """
  def task_is_ready(self, task):
    self._readyTasks.append(task)

  """
  This function is called by tasks at the beginning of their 'run'
  function
  """
  def task_is_running(self, task):
    # only print the description when 'showDescriptions' is True
    if self._showDescriptions:
      # format the output string
      text = "[Starting '" + task.get_name() + "'] " + task.describe()
      # print
      self.__print(text)
    # show progress
    self.__print_progress()

  """
  This is called by a Task when it has completed execution
  This is only called by tasks that are listed as dependencies
  """
  def task_is_done(self, task):
    self._tasks.remove(task)
    self._runningTasks.remove(task)
    # only print the description when 'showDescriptions' is True
    if self._showDescriptions:
      # format the output string
      text = "[Completed '" + task.get_name() + "'] " + task.describe()
      # print
      self.__print(text)
    # show progress
    self.__print_progress()

  """
  This function is called by a task when an error code is returned from
  the task
  """
  def task_error(self, task, errors):
    # format the output string
    text = "[" + task.get_name() + "] ERROR: " + task.describe()
    if type(errors) == int:
      text += "\n  Return: " + str(errors)
    else:
      text += "\n  Message: " + str(errors)
    if USE_TERM_COLOR:
      text = colored(text, 'red')
    # print
    self.__print(text)
    # kill
    os._exit(-1)

  """
  This runs all tasks in dependency order without running more than
  'numProcs' processes at one time
  """
  def run_tasks(self):
    # ignore empty call
    if not self._tasks: # not empty check
      return

    # set task settings
    for task in self._tasks:
      # tell the tasks to actually run (optionally)
      task.set_runnable(self._runTasks)
      # ask the tasks to report if they are ready to run
      # (root tasks)
      if task.ready():
        self.task_is_ready(task)

    # pre-compute some numbers for statistics
    self._totalTasks = len(self._tasks)

    # run all tasks until there is none left
    while self._tasks: # not empty check
      # wait for an available task to run
      if not self._readyTasks:
        time.sleep(0.25)  # 250ms
        continue
      # wait for an available process slot
      while len(self._runningTasks) >= self._numProcs:
        time.sleep(0.25)  # 250ms
      # get the next ready task
      task = self._readyTasks[0]
      self._readyTasks.remove(task)
      self._runningTasks.append(task)
      # run it
      task.start()

  """
  This function is called by the manager to show the progress in the
  output
  """
  def __print_progress(self):
    # show progress (optionally)
    if self._showProgress:
      # generate numbers
      total = self._totalTasks
      done = total - len(self._tasks)
      started = done + len(self._runningTasks);
      done_percent = int(round((done / float(total)) * 100.00, 0))
      started_percent = int(round((started / float(total)) * 100.00, 0))

      # format the output string
      text = ("{0:d}% Completed ({1:d} of {2:d}) {3:d}% Started "
              "({4:d} of {5:d})").format(done_percent, done, total,
                                         started_percent, started,
                                         total)
      text = ("{0:d}% ({1:d}) Completed; {2:d}% ({3:d}) Started; "
              "({4:d} Total)").format(done_percent, done,
                                      started_percent, started,
                                      total)
      if USE_TERM_COLOR:
        text = colored(text, 'green')

      # print
      self.__print(text)

  """
  This function is used to print a message to the output in a thread safe
  manner
  """
  def __print(self, *args, **kwargs):
    self._printLock.acquire(True)
    print(*args, **kwargs)
    self._printLock.release()
