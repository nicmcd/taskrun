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
import os
import random
import signal
import threading
import time
from .failure_mode import FailureMode
from .task import Task


class TaskManager:
  """
  This class manages a group of tasks
  """

  def __init__(self, resource_manager=None, observers=None,
               failure_mode=FailureMode.AGGRESSIVE_FAIL,
               priority_levels=16):
    """
    Constructs a TaskManager object

    Args:
      resource_manager (ResourceManager) : the resource manager to use
      observers (Observer)               : a collection of observers to user
    """

    self._running = False
    self._waiting_tasks = []
    assert isinstance(priority_levels, int) and priority_levels > 0, \
      'priority_levels must be an int > 0'
    self._priority_levels = priority_levels
    self._ready_tasks = [[] for x in range(self._priority_levels)]
    self._running_tasks = []
    self._filter_tasks = []
    self._resource_manager = resource_manager
    self._observers = []
    if observers:
      self._observers = list(observers)
    self._condition_variable = threading.Condition()
    self._failure_mode = FailureMode.create(failure_mode)
    self._failed = False
    self._killed = False
    self._last_sigint_time = (datetime.datetime.now() -
                              datetime.timedelta(seconds = 5))
    self._pid = os.getpid()

  def add_observer(self, observer):
    """
    This adds an observer to the list of observers
    """
    self._observers.append(observer)

  def add_task(self, task):
    """
    This adds a task to this manager

    Args:
      task (Task) : the task to add
    """
    assert isinstance(task, Task)
    assert self._running is False
    self._waiting_tasks.append(task)

    # pass info to the observer
    for observer in self._observers:
      observer.task_added(task)

  def get_task(self, name):
    """
    Returns a waiting task specified by name
    Undefined behavior if multiple equal named tasks exist

    Args:
      name (str) : the name of the task
    """
    assert self._running is False
    for task in self._waiting_tasks:
      if task.name == name:
        return task
    return None

  def randomize(self):
    """
    This randomizes the task list
    """
    assert self._running is False

    if len(self._waiting_tasks) > 1:
      # get random samples
      random_indices = []
      random_samples = []
      for _ in range(min(5, len(self._waiting_tasks))):
        random_index = random.choice(range(len(self._waiting_tasks)))
        random_indices.append(random_index)
        random_samples.append(self._waiting_tasks[random_index].name)

      # shuffles until unique
      while True:
        # shuffle
        random.shuffle(self._waiting_tasks)

        # compare samples
        match = True
        for index, random_index in enumerate(random_indices):
          random_sample = random_samples[index]
          shuffled_sample = self._waiting_tasks[random_index].name
          if shuffled_sample != random_sample:
            match = False
            break
        if not match:
          break

  def _probe_ready(self):
    """
    This method probes the waiting tasks to see if they are ready
    """
    assert self._running is True
    temp_ready = []
    for task in self._waiting_tasks:
      if task.ready():
        temp_ready.append(task)
    for task in temp_ready:
      self.task_ready(task)

  def task_ready(self, task):
    """
    This is called by a Task when it becomes ready to run

    Args:
      task (Task) : the task that is now ready to run
    """

    assert self._running is True
    with self._condition_variable:
      # check if this task is in the filter list
      if task in self._filter_tasks:
        assert task not in self._waiting_tasks
        self._filter_tasks.remove(task)

      else:
        # transfer from waiting to ready list
        self._waiting_tasks.remove(task)
        assert task.priority < self._priority_levels, \
          'task.priority must be less than priority_levels'
        self._ready_tasks[task.priority].append(task)

      # notify waiting threads
      self._condition_variable.notify()

  def _task_started(self, task):
    """
    This is called when a Task has started execution

    WARNING: this method must be called while locked on the condition variable

    Args:
      task (Task) : the task that completed
    """
    assert self._running is True

    # notify observer
    for observer in self._observers:
      observer.task_started(task)

  def _task_bypassed(self, task):
    """
    This is called when a Task has been bypassed

    WARNING: this method must be called while locked on the condition variable

    Args:
      task (Task) : the task that bypassed
    """
    assert self._running is True

    # notify observer
    for observer in self._observers:
      observer.task_bypassed(task)

    # clean up the task
    self._task_done(task)

  def task_completed(self, task):
    """
    This is called when a Task has completed execution

    Args:
      task (Task) : the task that completed
    """
    assert self._running is True

    with self._condition_variable:
      # pass info to the observer
      for observer in self._observers:
        observer.task_completed(task)

      # clean up the task
      self._task_done(task)

  def task_failed(self, task, errors):
    """
    This function is called by a task when an error code is returned from
    the task

    Args:
      task (Task) : the task that encountered errors
    """
    assert self._running is True

    self._task_error(task, errors)

  def task_killed(self, task):
    """
    This function is called by a task when it has been killed

    Args:
      task (Task) : the task that was killed
    """
    assert self._running is True

    self._task_error(task, None)

  def _task_error(self, task, errors):
    """
    This function is called when a task fails or is killed

    Args:
      task (Task) : the task that failed or was killed
    """
    assert self._running is True
    self._failed = True

    # handle the failure
    with self._condition_variable:
      # handle failure based on failure mode
      if self._failure_mode is FailureMode.AGGRESSIVE_FAIL:
        self._kill_running()
        self._clear_waiting_and_ready()
      elif self._failure_mode is FailureMode.PASSIVE_FAIL:
        self._clear_waiting_and_ready()
      elif self._failure_mode is FailureMode.ACTIVE_CONTINUE:
        self._remove_dependent_tasks(task)
      elif self._failure_mode is FailureMode.BLIND_CONTINUE:
        pass
      else:
        assert False, "programmer error, fire somebody!"

      # pass info to the observer
      for observer in self._observers:
        if task.killed:
          observer.task_killed(task)
        else:
          observer.task_failed(task, errors)

      # clean up the task
      self._task_done(task)

  def _kill_running(self):
    """
    Kills all running tasks
    """
    # kill all the currently running tasks
    if not self._killed:
      self._killed = True
      for task in self._running_tasks:
        task.kill()

  def _clear_waiting_and_ready(self):
    """
    Clears the waiting and ready tasks lists. Adds the tasks to the filtered
    list.
    """
    # clear out waiting and ready lists
    self._filter_tasks.extend(self._waiting_tasks)
    self._waiting_tasks = []
    for priority in range(self._priority_levels):
      self._filter_tasks.extend(self._ready_tasks[priority])
      self._ready_tasks[priority] = []

  def _remove_dependent_tasks(self, task):
    """
    Removes the dependent tasks of the specified task. Adds the tasks to the
    filtered list.
    """
    # remove all tasks that depend on this task (BFS)
    visit = []
    visit.extend(task.get_dependents())
    visited = set()
    while len(visit) > 0:
      curr = visit.pop()
      for priority in range(self._priority_levels):
        assert curr not in self._ready_tasks[priority]
      assert curr not in self._running_tasks
      visited.add(curr)
      for dep in curr.get_dependents():
        if dep not in visited:
          visit.append(dep)
      if curr in self._waiting_tasks:
        self._waiting_tasks.remove(curr)
        self._filter_tasks.append(curr)

  def _task_done(self, task):
    """
    This method is called by task_completed and task_error.
    This method removes the task from the running list and gives back all
    resources it consumed.

    WARNING: this method must be called while locked on the condition variable.

    Args:
      task (Task) : the task that finished
    """
    assert self._running is True

    # remove task from running lists
    self._running_tasks.remove(task)

    # give back resources
    if not task.bypass:
      if self._resource_manager is not None:
        self._resource_manager.done(task)

    # notify waiting thread
    self._condition_variable.notify()

  def _terminate(self):
    """
    Executes the procedure for graceful forced shutdown.
    """
    assert self._running is True
    self._failed = True
    with self._condition_variable:
      self._kill_running()
      self._clear_waiting_and_ready()
      self._condition_variable.notify()

  def _handle_signal(self, signum):
    # Kills the process if the task manager's known pid does not match the pid
    # of this process. This is for the case where a task uses subprocess to
    # fork the process but the start_new_session handling hasn't been
    # completed. It is important to kill the process (exit) so that the signal
    # isn't ignored.
    if os.getpid() != self._pid:
      os._exit(-1)  # pylint: disable=protected-access
      return

    if signum == signal.SIGINT:
      # Print a newline after the ^C that the user's shell printed
      print()

      # Tracks the time of the last signal to create a SIGINT time guard of 3s.
      now = datetime.datetime.now()
      delta = (now - self._last_sigint_time).total_seconds()
      self._last_sigint_time = now
      if delta >= 3.0:
        print("Press Ctrl-C again within 3 seconds to terminate")
        return

    # Resets signal handlers to default
    TaskManager._reset_signal_handlers()

    # Create a new thread to perform the termination. A separate thread is
    # needed because this signal handler is running within the main thread
    # that may or may not have the condition variable acquired. A separate
    # thread allows this to behave just like a failing task.
    threading.Thread(target=self._terminate).start()

  def _set_signal_handlers(self):
    """
    Sets the signal handlers for SIGINT and SIGTERM to gracefully shutdown when
    received. SIGINT also includes a 3 second guard window.
    """
    ignore_signal = False
    def handler(signum, _):
      # Ignores signal if this function is already handling a signal.
      nonlocal ignore_signal
      if ignore_signal:
        return
      ignore_signal = True
      self._handle_signal(signum)
      ignore_signal = False

    # Installs 'handler' as the signal handler for SIGINT and SIGTERM
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

  @staticmethod
  def _reset_signal_handlers():
    """
    Resets the changed signal handlers to the default handlers.
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)


  def run_tasks(self):
    """
    This runs all tasks in dependency order and executing with the
    ResourceManager's discretion.

    This must be run by the main thread. Will overwrite SIGINT and SIGTERM
    signal handlers.
    """
    assert self._running is False
    self._running = True
    self._failed = False

    # sets the signal handlers for graceful shutdown
    self._set_signal_handlers()

    # ask the tasks if they are ready to run (find root tasks)
    self._probe_ready()

    # inform all observers of run starting
    for observer in self._observers:
      observer.run_starting()

    # run all tasks until there is none left
    while True:
      # use the condition variable for pausing/resuming and locking
      with self._condition_variable:
        # check if we are done
        if (len(self._waiting_tasks) == 0 and
            sum(map(len, self._ready_tasks)) == 0 and
            len(self._running_tasks) == 0): # and
            #len(self._filter_tasks) == 0):
          break

        # wait for a ready task
        if sum(map(len, self._ready_tasks)) == 0:
          self._condition_variable.wait()
          continue

        # find the highest priority task in FIFO order within priority levels
        next_task = None
        for priority in reversed(range(self._priority_levels)):
          if len(self._ready_tasks[priority]) > 0:
            next_task = self._ready_tasks[priority][0]
            break
        assert next_task is not None

        # if not being bypassed, check if there enough resources to run the task
        #  on success, the resource will have been used
        if (not next_task.bypass and
            self._resource_manager is not None and
            self._resource_manager.start(next_task) is False):
          self._condition_variable.wait()
          continue

        # transfer from ready to running
        self._ready_tasks[next_task.priority].remove(next_task)
        self._running_tasks.append(next_task)

        # signal started or bypassed
        if not next_task.bypass:
          self._task_started(next_task)
        else:
          self._task_bypassed(next_task)

      # at this point, the next_task is either being bypassed or there is enough
      #  resources to execute the task

      # run it
      next_task.start()

      # give up execution to other threads/processes
      #  this allows tasks to start
      time.sleep(0.000001)

    # turn off
    self._running = False

    # inform all observers of run completion
    for observer in self._observers:
      observer.run_complete()

    # resets the signal handlers to the defaults
    TaskManager._reset_signal_handlers()

    # return True iff all tasks reported success, False otherwise
    return not self._failed
