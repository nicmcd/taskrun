"""
 * Copyright (c) 2012-2016, Nic McDonald
 * All rights reserved.
 *
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
 * - Neither the name of prim nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
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
# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import sys

from .Observer import Observer


# conditionally import the termcolor package, it's OK if it doesn't exist
try:
  USE_TERM_COLOR = True
  from termcolor import colored
except ImportError:
  USE_TERM_COLOR = False
USE_TERM_COLOR &= sys.stdout.isatty()


class VerboseObserver(Observer):
  """
  This class is an observer for just printing what is happening
  """

  def __init__(self, show_start=True, show_bypass=True, show_complete=True,
               show_fail=True, show_description=True, show_progress=True):
    """
    Constructs an Observer

    Args:
      show_start (bool)     : print when tasks start
      show_bypass (bool)    : print when tasks bypass
      show_complete (bool)   : print when tasks complete
      show_fail (bool)      : print when tasks fail
      show_description (bool) : add the task description to the print out
    """

    super(VerboseObserver, self).__init__()
    self._show_start = show_start
    self._show_bypass = show_bypass
    self._show_complete = show_complete
    self._show_fail = show_fail
    self._show_description = show_description
    self._show_progress = show_progress
    self._total_tasks = 0
    self._finished_tasks = 0

  def task_added(self, task):
    """
    See Observer.task_added()
    This class used this only to create a count
    """
    self._total_tasks += 1

  def task_started(self, task):
    """
    See Observer.task_started()
    """

    if self._show_start:
      # format the output string
      text = '[Started: {0}]'.format(task.name)
      # optionally add the description
      if self._show_description:
        text += ' {0}'.format(task.describe())
      # print
      print(text)

  def task_bypassed(self, task):
    """
    See Observer.task_bypassed()
    """

    self._finished_tasks += 1
    if self._show_bypass:
      # format the output string
      text = '[Bypassed: {0}]'.format(task.name)
      # optionally add the description
      if self._show_description:
        text += ' {0}'.format(task.describe())
      # print
      if USE_TERM_COLOR:
        text = colored(text, 'yellow')
      print(text)

    self._progress()

  def task_completed(self, task):
    """
    See Observer.task_completed()
    """

    self._finished_tasks += 1
    if self._show_complete:
      # format the output string
      text = '[Completed: {0}]'.format(task.name)
      # optionally add the description
      if self._show_description:
        text += ' {0}'.format(task.describe())
      # print
      if USE_TERM_COLOR:
        text = colored(text, 'green')
      print(text)

    self._progress()

  def task_failed(self, task, errors):
    """
    See Observer.task_failed()
    """

    self._finished_tasks += 1
    if self._show_fail:
      # format the output string
      text = '[Failed: {0}]'.format(task.name)
      # optionally add the description
      if self._show_description:
        text += ' {0}'.format(task.describe())
      # append the error
      if isinstance(errors, int):
        text += '\n  Return: {0}'.format(str(errors))
      else:
        text += '\n  Message: {0}'.format(str(errors))
      if USE_TERM_COLOR:
        text = colored(text, 'red')
      # print
      print(text)

    self._progress()

  def _progress(self):
    """
    This prints the progress of the tasks
    """

    if self._show_progress:
      text = '[Progress: {0:3.2f}% {1}/{2}]'.format(
        self._finished_tasks / self._total_tasks,
        self._finished_tasks, self._total_tasks)
      if USE_TERM_COLOR:
        text = colored(text, 'magenta')
      print(text)
