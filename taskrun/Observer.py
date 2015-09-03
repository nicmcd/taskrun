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
This defines the an Observer, one who watches what the Manager is executing.
"""
class Observer(object):

  def __init__(self, show_starting=True, show_completed=True):
    self._print_lock = threading.Lock()
    self._show_starting = show_starting
    self._show_completed = show_completed

  def task_starting(self, task):
    # only print the description when 'showDescriptions' is True
    if self._show_starting:
      # format the output string
      text = "[Starting '" + task.get_name() + "'] " + task.describe()
      # print
      self.__print(text)

  def task_completed(self, task):
    # only print the description when 'showDescriptions' is True
    if self._show_completed:
      # format the output string
      text = "[Completed '" + task.get_name() + "'] " + task.describe()
      # print
      self.__print(text)

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

  """
  This function is called to show the progress in the output
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
    self._print_lock.acquire(True)
    print(*args, **kwargs)
    self._print_lock.release()
