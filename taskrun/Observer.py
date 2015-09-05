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

  def __init__(self, show_started=True, show_bypassed=True,
               show_completed=True, show_error=True):
    """
    Constructs an Observer

    Args:
      show_started (bool)   : print description when tasks start
      show_bypassed (bool)  : print description when tasks bypass
      show_completed (bool) : print description when tasks complete
    """
    self._show_started = show_started
    self._show_bypassed = show_bypassed
    self._show_completed = show_completed
    self._show_error = show_error

  def task_started(self, task):
    """
    Notification of a task starting

    Args:
      task (Task): the task that is now starting
    """

    if self._show_started:
      # format the output string
      text = "[Started '" + task.name + "'] " + task.describe()
      # print
      print(text)

  def task_bypassed(self, task):
    """
    Notification of a task bypass

    Args:
      task (Task): the task that is bypassed
    """

    if self._show_bypassed:
      # format the output string
      text = "[Bypassed '" + task.name + "'] " + task.describe()
      # print
      print(text)

  def task_completed(self, task):
    """
    Notification of a task completion

    Args:
      task (Task): the task that completed
    """

    if self._show_completed:
      # format the output string
      text = "[Completed '" + task.name + "'] " + task.describe()
      # print
      print(text)

  def task_error(self, task, errors):
    """
    Notification of task failure

    Args:
      task (Task): the task that failed
    """

    if self._show_error:
      # format the output string
      text = "[" + task.name + "] ERROR: " + task.describe()
      if type(errors) == int:
        text += "\n  Return: " + str(errors)
      else:
        text += "\n  Message: " + str(errors)
      if USE_TERM_COLOR:
        text = colored(text, 'red')
      # print
      print(text)
