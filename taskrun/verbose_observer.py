"""
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
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
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
import datetime
import sys
import time

from .observer import Observer


# conditionally import the termcolor package, it's OK if it doesn't exist
try:
  USE_TERM_COLOR = True
  from termcolor import colored
except ImportError:
  USE_TERM_COLOR = False
USE_TERM_COLOR &= sys.stdout.isatty()


class VerboseObserver(Observer):
  """
  This class is an observer for printing what is happening
  """

  TIMER_DEFAULT = True
  LOG_DEFAULT = None
  SHOW_STARTS_DEFAULT = True
  SHOW_COMPLETES_DEFAULT = True
  SHOW_BYPASSES_DEFAULT = True
  SHOW_FAILURES_DEFAULT = True
  SHOW_KILLS_DEFAULT = False
  SHOW_PROGRESS_DEFAULT = True
  SHOW_SUMMARY_DEFAULT = True
  SHOW_DESCRIPTIONS_DEFAULT = False
  SHOW_CURRENT_TIME_DEFAULT = False

  def __init__(self, timer=TIMER_DEFAULT, log=LOG_DEFAULT,
               show_starts=SHOW_STARTS_DEFAULT,
               show_completes=SHOW_COMPLETES_DEFAULT,
               show_bypasses=SHOW_BYPASSES_DEFAULT,
               show_failures=SHOW_FAILURES_DEFAULT,
               show_kills=SHOW_KILLS_DEFAULT,
               show_progress=SHOW_PROGRESS_DEFAULT,
               show_summary=SHOW_SUMMARY_DEFAULT,
               show_descriptions=SHOW_DESCRIPTIONS_DEFAULT,
               show_current_time=SHOW_CURRENT_TIME_DEFAULT):
    """
    Constructs an Observer

    Note: if a task fails or is killed and it is set to be shown, the
          description is always added
    """
    super().__init__()
    self._total_tasks = 0
    self._finished_tasks = 0
    self._successful_tasks = 0
    self._bypassed_tasks = 0
    self._failed_tasks = 0
    self._killed_tasks = 0
    self._timer = timer
    self._times = {}
    self._start_time = None
    self._end_time = None
    self._log = log
    self._show_starts = show_starts
    self._show_completes = show_completes
    self._show_bypasses = show_bypasses
    self._show_failures = show_failures
    self._show_kills = show_kills
    self._show_progress = show_progress
    self._show_summary = show_summary
    self._show_descriptions = show_descriptions
    self._show_current_time = show_current_time

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

    if self._timer:
      self._times[task] = time.time()

    if self._show_starts:
      text = ''
      if self._show_current_time:
        text += f'{_now_string()} '
      text += f'[Started: {task.name}]'
      if self._show_descriptions:
        text += f' {task.describe()}'
      if self._log:
        print(text, file=self._log)
      print(text)

  def task_bypassed(self, task):
    """
    See Observer.task_bypassed()
    """

    self._finished_tasks += 1
    self._bypassed_tasks += 1
    if self._show_bypasses:
      text = ''
      if self._show_current_time:
        text += f'{_now_string()} '
      text += f'[Bypassed: {task.name}]'
      if self._show_descriptions:
        text += f' {task.describe()}'
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'yellow')
      print(text)
      self._progress()

  def task_completed(self, task):
    """
    See Observer.task_completed()
    """

    if self._timer:
      task_time = time.time() - self._times.pop(task)

    self._finished_tasks += 1
    self._successful_tasks += 1
    if self._show_completes:
      text = ''
      if self._show_current_time:
        text += f'{_now_string()} '
      text += f'[Completed: {task.name}'
      if self._timer:
        text += f' {_time_string(task_time)}'
      text += ']'
      if self._show_descriptions:
        text += f'\n  {task.describe()}'
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'green')
      print(text)
      self._progress()

  def task_failed(self, task, errors):
    """
    See Observer.task_failed()
    """

    if self._timer:
      task_time = time.time() - self._times.pop(task)

    self._finished_tasks += 1
    self._failed_tasks += 1
    if self._show_failures:
      text = ''
      if self._show_current_time:
        text += f'{_now_string()} '
      text += f'[Failed: {task.name}'
      if self._timer:
        text += f' {_time_string(task_time)}'
      text += ']'
      text += f'\n  Description: {task.describe()}'
      if isinstance(errors, int):
        text += f'\n  Return: {str(errors)}'
      else:
        text += f'\n  Message: {str(errors)}'
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'red')
      print(text)
      self._progress()

  def task_killed(self, task):
    """
    See Observer.task_killed()
    """

    if self._timer:
      task_time = time.time() - self._times.pop(task)

    self._finished_tasks += 1
    self._killed_tasks += 1
    if self._show_kills:
      text = ''
      if self._show_current_time:
        text += f'{_now_string()} '
      text += f'[Killed: {task.name}'
      if self._timer:
        text += f' {_time_string(task_time)}'
      text += ']'
      text += f'\n  Description: {task.describe()}'
      if self._log:
        print(text, file=self._log)
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

    self._end_time = time.time()

    self._summary()

  def _progress(self):
    """
    This prints the progress of the tasks
    """

    if self._show_progress:
      text = ''
      if self._show_current_time:
        text += f'{_now_string()} '
      text += '[Progress: {0:3.2f}% {1}/{2}'.format(
        self._finished_tasks / self._total_tasks * 100.0,
        self._finished_tasks, self._total_tasks)
      if self._timer:
        run_time = time.time() - self._start_time
        exec_rate = (self._successful_tasks + self._failed_tasks +
                     self._killed_tasks) / run_time
        if exec_rate == 0.0:
          text += ' INFINITY'
        else:
          est_time = (self._total_tasks - self._finished_tasks) / exec_rate
          text += f' {_time_string(est_time)}'
      text += ']'
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'magenta')
      print(text)

  def _summary(self):
    """
    This prints the summary of the tasks' execution
    """

    if self._show_summary:
      text = '\nTask Summary:'
      if self._log:
        print(text, file=self._log)
      print(text)

      if self._show_current_time:
        text = f'  Now        : {_now_string()}'
        if self._log:
          print(text, file=self._log)
        print(text)

      text = f'  Total      : {self._total_tasks}'
      if self._log:
        print(text, file=self._log)
      print(text)

      text = f'  Time       : {_time_string(self._end_time - self._start_time)}'
      if self._log:
        print(text, file=self._log)
      print(text)

      text = f'  Successful : {self._successful_tasks}'
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'green')
      print(text)

      text = f'  Bypassed   : {self._bypassed_tasks}'
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'yellow')
      print(text)

      text = f'  Failed     : {self._failed_tasks}'
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'red')
      print(text)

      text = f'  Killed     : {self._killed_tasks}'
      if self._log:
        print(text, file=self._log)
      if USE_TERM_COLOR:
        text = colored(text, 'red')
      print(text)

def _time_string(total_seconds):
  """
  This returns a string representing the elapsed time given

  Args:
    total_seconds: the elapsed time in seconds
  """

  days, rem = divmod(total_seconds, 60 * 60 * 24)
  hours, rem = divmod(rem, 60 * 60)
  minutes, seconds = divmod(rem, 60)
  if days > 0:
    return f'{int(days)}d:{int(hours)}h:{int(minutes)}m:{int(seconds)}s'
  if hours > 0:
    return f'{int(hours)}h:{int(minutes)}m:{int(seconds)}s'
  if minutes > 0:
    return f'{int(minutes)}m:{int(seconds)}s'
  return f'{int(seconds)}s'


def _now_string():
  """This returns a formatted string for the current date and time."""
  return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
