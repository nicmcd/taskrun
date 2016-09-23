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
from enum import Enum, unique
import datetime
import sys
import time

from .Observer import Observer


# conditionally import the termcolor package, it's OK if it doesn't exist
try:
  USE_TERM_COLOR = True
  from termcolor import colored
except ImportError:
  USE_TERM_COLOR = False
USE_TERM_COLOR &= sys.stdout.isatty()


@unique
class Verbosity(Enum):
  """
  This class creates sets verbosity for the VerbosityObserver
  """

  NONE = 0  # no output
  FAILURE = 1  # only failures
  START = 2  # starts and failures
  COMPLETE = 3  # completes, bypasses, and failures
  ALL = 4  # starts, completes, bypasses, failures, and progress


class VerboseObserver(Observer):
  """
  This class is an observer for just printing what is happening
  """

  def __init__(self, verbosity=Verbosity.ALL, description=False, summary=True,
               time=True, log=None):
    """
    Constructs an Observer

    Note: descriptions are always shown on error

    Args:
      verbosity (Verbosity) : the verbosity mode
      description (bool)    : add the task description to the print out
    """

    super(VerboseObserver, self).__init__()
    self._verbosity = verbosity
    self._description = description
    self._total_tasks = 0
    self._finished_tasks = 0
    self._successful_tasks = 0
    self._bypassed_tasks = 0
    self._failed_tasks = 0
    self._summary = summary
    self._time = time
    self._times = {}
    self._start_time = None
    self._log = log

    assert isinstance(verbosity, Verbosity), \
      'verbosity must be a Verbosity type'

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

    if self._time:
      self._times[task] = time.time()

    if (self._verbosity is Verbosity.START or
        self._verbosity is Verbosity.ALL):
      # format the output string
      text = '[Started: {0}]'.format(task.name)
      # optionally add the description
      if self._description:
        text += ' {0}'.format(task.describe())
      # log
      if self._log:
        print(text, file=self._log)
      # print
      print(text)

  def task_bypassed(self, task):
    """
    See Observer.task_bypassed()
    """

    self._finished_tasks += 1
    self._bypassed_tasks += 1
    if (self._verbosity is Verbosity.COMPLETE or
        self._verbosity is Verbosity.ALL):
      # format the output string
      text = '[Bypassed: {0}]'.format(task.name)
      # optionally add the description
      if self._description:
        text += ' {0}'.format(task.describe())
      # log
      if self._log:
        print(text, file=self._log)
      # print
      if USE_TERM_COLOR:
        text = colored(text, 'yellow')
      print(text)

    self._progress()

  def task_completed(self, task):
    """
    See Observer.task_completed()
    """

    if self._time:
      task_time = time.time() - self._times.pop(task)

    self._finished_tasks += 1
    self._successful_tasks += 1
    if (self._verbosity is Verbosity.COMPLETE or
        self._verbosity is Verbosity.ALL):
      # format the output string
      text = '[Completed: {0}'.format(task.name)
      # optionally add the time
      if self._time:
        text += ' {0}'.format(_time_string(task_time))
      text += ']'
      # optionally add the description
      if self._description:
        text += '\n  {0}'.format(task.describe())
      # log
      if self._log:
        print(text, file=self._log)
      # print
      if USE_TERM_COLOR:
        text = colored(text, 'green')
      print(text)

    self._progress()

  def task_failed(self, task, errors):
    """
    See Observer.task_failed()
    """

    if self._time:
      task_time = time.time() - self._times.pop(task)

    self._finished_tasks += 1
    self._failed_tasks += 1
    if self._verbosity is not Verbosity.NONE:
      # format the output string
      text = '[Failed: {0}'.format(task.name)
      # optionally add the time
      if self._time:
        text += ' {0}'.format(_time_string(task_time))
      text += ']'
      # add the description
      text += '\n  Description: {0}'.format(task.describe())
      # append the error
      if isinstance(errors, int):
        text += '\n  Return: {0}'.format(str(errors))
      else:
        text += '\n  Message: {0}'.format(str(errors))
      # log
      if self._log:
        print(text, file=self._log)
      # print
      if USE_TERM_COLOR:
        text = colored(text, 'red')
      print(text)

    self._progress()

  def run_starting(self):
    """
    See Observer.run_starting()
    """
    self._start_time = time.time()

  def run_complete(self):
    """
    See Observer.run_complete()
    """
    if self._summary:
      self._show_summary()

  def _progress(self):
    """
    This prints the progress of the tasks
    """

    if self._verbosity is Verbosity.ALL:
      text = '[Progress: {0:3.2f}% {1}/{2}'.format(
        self._finished_tasks / self._total_tasks * 100.0,
        self._finished_tasks, self._total_tasks)
      # optionally add the estimated time to complete
      if self._time:
        run_time = time.time() - self._start_time
        exec_rate = self._finished_tasks / run_time
        est_time = (self._total_tasks - self._finished_tasks) / exec_rate
        text += ' {0}'.format(_time_string(est_time))
      text += ']'
      # log
      if self._log:
        print(text, file=self._log)
      # print
      if USE_TERM_COLOR:
        text = colored(text, 'magenta')
      print(text)

  def _show_summary(self):
    """
    This prints the summary of the tasks' execution
    """

    if (self._verbosity is Verbosity.COMPLETE or
        self._verbosity is Verbosity.ALL):
      text = '\nTask Summary:'
      if self._log:
        print(text, file=self._log)
      print(text)

      text = '  Total      : {0}'.format(self._total_tasks)
      if self._log:
        print(text, file=self._log)
      print(text)

      text = '  Successful : {0}'.format(self._successful_tasks)
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'green')
      print(text)

      text = '  Bypassed   : {0}'.format(self._bypassed_tasks)
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'yellow')
      print(text)

      text = '  Failed     : {0}'.format(self._failed_tasks)
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'red')
      print(text)

def _time_string(time):
  """
  This returns a string representing the elapsed time given

  Args:
    time: the elapsed time
  """

  days, rem = divmod(time, 60 * 60 * 24)
  hours, rem = divmod(rem, 60 * 60)
  minutes, seconds = divmod(rem, 60)
  if days > 0:
    return '{0}d:{1}h:{2}m:{3}s'.format(
      int(days), int(hours), int(minutes), int(seconds))
  elif hours > 0:
    return '{0}h:{1}m:{2}s'.format(
      int(hours), int(minutes), int(seconds))
  elif minutes > 0:
    return '{0}m:{1}s'.format(
      int(minutes), int(seconds))
  else:
    return '{0}s'.format(
      int(seconds))
