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

class Observer:
  """
  This defines the an Observer, one who watches what the Manager is executing.
  This class is meant to be overridden by subclasses that want a custom way to
  monitor observance of tasks starting and completing.
  """

  def task_added(self, task):
    """
    Notification of a task added to the TaskManager

    Args:
      task (Task): the task that is now starting
    """

  def task_started(self, task):
    """
    Notification of a task starting

    Args:
      task (Task): the task that is now starting
    """

  def task_bypassed(self, task):
    """
    Notification of a task bypass

    Args:
      task (Task): the task that is bypassed
    """

  def task_completed(self, task):
    """
    Notification of a task completion

    Args:
      task (Task): the task that completed
    """

  def task_failed(self, task, errors):
    """
    Notification of task failure

    Args:
      task (Task): the task that failed
      errors     : an errors to be reported
    """

  def task_killed(self, task):
    """
    Notification of a task being killed

    Args:
      task (Task): the task that failed
    """

  def run_starting(self):
    """
    Notification of run starting
    """

  def run_complete(self):
    """
    Notification of run completion
    """
