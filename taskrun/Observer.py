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
import sys

# conditionally import the termcolor package, it's OK if it doesn't exist
try:
  USE_TERM_COLOR = True
  from termcolor import colored
except ImportError:
  USE_TERM_COLOR = False
USE_TERM_COLOR &= sys.stdout.isatty()


class Observer(object):
  """
  This defines the an Observer, one who watches what the Manager is executing.
  This class is meant to be overridden by subclasses that want a custom way to
  monitor observance of tasks starting and completing.
  """

  def __init__(self, show_starting=True, show_completed=True):
    """
    Constructs an Observer

    Args:
      show_starting (bool) : print description when tasks start
      show_completed (bool): print description when tasks complete
    """
    self._show_starting = show_starting
    self._show_completed = show_completed
    self._print_lock = threading.Lock()

  def task_starting(self, task):
    """
    Notification of a task starting

    Args:
      task (Task): the task that is now starting
    """

    # only print the description when 'showDescriptions' is True
    if self._show_starting:
      # format the output string
      text = "[Starting '" + task.name + "'] " + task.describe()
      # print
      self.__print(text)

  def task_completed(self, task):
    """
    Notification of a task completion

    Args:
      task (Task): the task that completed
    """

    # only print the description when 'showDescriptions' is True
    if self._show_completed:
      # format the output string
      text = "[Completed '" + task.name + "'] " + task.describe()
      # print
      self.__print(text)

  def task_error(self, task, errors):
    """
    Notification of task failure

    Args:
      task (Task): the task that failed
    """

    # format the output string
    text = "[" + task.name + "] ERROR: " + task.describe()
    if type(errors) == int:
      text += "\n  Return: " + str(errors)
    else:
      text += "\n  Message: " + str(errors)
    if USE_TERM_COLOR:
      text = colored(text, 'red')
    # print
    self.__print(text)

  def __print(self, *args, **kwargs):
    """
    Thread safe printing

    Args:
      *args    : passed to print()
      **kwargs : passed to print()
    """

    self._print_lock.acquire(True)
    print(*args, **kwargs)
    self._print_lock.release()
