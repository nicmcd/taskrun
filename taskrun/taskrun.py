"""
Copyright (c) 2013, Nic McDonald
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

from __future__ import print_function # backwards print compatibility
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

# this declares the version
VERSION = (1, 0, 0)

"""
This defines one task to be executed
Each task has a set of dependencies, which are other tasks
Each task notifies all tasks that are dependent on it upon completion
"""
class Task(threading.Thread):

    """
    Tasks should not be directly instantiated. The user should use the manager.task_new() function
    """
    def __init__(self, manager, name, command, output=None):
        threading.Thread.__init__(self)
        self._manager = manager
        self._name = name
        self._command = command
        self._output = output
        self._dependencies = []
        self._notifiees = []
        self._run = True
        self._accessLock = threading.Lock()

    def name(self):
        return self._name

    def command(self):
        return self._command

    def output(self):
        return self._output

    """
    This function must be called BEFORE Manager.run_request_is() is called
    """
    def dependency_is(self, task):
        self._dependencies.append(task)
        task.__notifiee_is(self)

    def __notifiee_is(self, notifiee):
        self._notifiees.append(notifiee)

    def _run_is(self, run):
        self._run = run

    """
    This function is only called by the Manager
    """
    def _ready_request_is(self):
        if not self._dependencies: # test for empty
            self._manager._ready_task_is(self)

    """
    This function is called by dependent tasks when they complete
    """
    def _done_task_is(self, task):
        self._dependencies.remove(task)
        if not self._dependencies: # test for empty
            self._manager._ready_task_is(self)

    """
    This function is called by the threading library after the class's 'Start' function is called
    """
    def run(self):

        # inform the manager that this task is now running
        self._manager._running_task_is(self)

        # run the command (optionally)
        if self._run:

            # execute the task command
            if self._output is not None:
                ofd = open(self._output, 'w')
            else:
                ofd = open('/dev/null', 'w')
            proc = subprocess.Popen(self._command, stdout=ofd, stderr=ofd, shell=True)

            # wait for the process to finish
            proc.wait()

            # close the output
            if self._output is not None:
                ofd.close()

            # check the return code
            ret = proc.returncode
            if ret != 0:
                self._manager._errored_task_is(self, ret)

        # inform the manager of task completion
        self._manager._done_task_is(self)

        # inform all notifiees of task completion
        for notifiee in self._notifiees:
            notifiee._done_task_is(self)


    """
    This nested class manages a group of tasks
    """
    class Manager():

        def __init__(self, numProcs=None, showCommands=True, runTasks=True, showProgress=True):
            self._numProcs = numProcs
            if not numProcs:
                self._numProcs = multiprocessing.cpu_count()
            self._printLock = threading.Lock()
            self._tasks = []
            self._readyTasks = []
            self._runningTasks = []
            self._printLock = threading.Lock()
            self._showCommands = showCommands
            self._runTasks = runTasks
            self._showProgress = showProgress

        """
        This is the effective constructor for a task
        It also adds the task to this manager instance
        """
        def task_new(self, name, command, output=None):
            task = Task(self, name, command, output)
            self._tasks.append(task)
            return task

        """
        This is called by a Task when it becomes ready to run
        """
        def _ready_task_is(self, task):
            self._readyTasks.append(task)

        """
        This is called by a Task when it has completed execution
        This is only called by tasks that are listed as dependencies
        """
        def _done_task_is(self, task):
            self._tasks.remove(task)
            self._runningTasks.remove(task)

        """
        This runs all tasks in dependency order without running more than 'numProcs'
        processes at one time
        """
        def run_request_is(self):

            # ignore empty call
            if not self._tasks: # not empty check
                return

            # set task settings
            for task in self._tasks:

                # tell the tasks to actually run their command (optionally)
                task._run_is(self._runTasks)

                # ask the tasks to report if they are already to run (root tasks)
                task._ready_request_is()

            # pre-compute some number for statistics
            totalTasks = len(self._tasks)

            # run all tasks until there is none left
            while self._tasks: # not empty check

                # wait for an available task to run
                if not self._readyTasks:
                    time.sleep(.1)
                    continue

                # wait for an available process slot
                while len(self._runningTasks) >= self._numProcs:
                    time.sleep(.1)

                # get the next ready task
                task = self._readyTasks[0]
                self._readyTasks.remove(task)
                self._runningTasks.append(task)

                # compute the number of remaining tasks before starting next task
                remainingTasks = len(self._tasks)

                # run it
                task.start()

                # show progress (optionally)
                if self._showProgress:
                    self.__print_progress(totalTasks, remainingTasks)

            # show progress (optionally)
            if self._showProgress:
                self.__print_progress(totalTasks, len(self._tasks))

        """
        This function is called by tasks at the beginning of their 'run' function
        """
        def _running_task_is(self, task):

            # only print the command when 'showCommands' is True
            if self._showCommands:

                # format the output string
                text = "[" + task.name() + "] " + task.command()
                if task.output():
                    text += " &> " + task.output()

                # print
                self.__print(text)

        """
        This function is called by a task when an error code is returned from the task
        """
        def _errored_task_is(self, task, code):

            # format the output string
            text = "[" + task.name() + "] ERROR: " + task.command()
            if task.output():
                text += " &> " + task.output()
            text += "\nReturned " + str(code)
            if USE_TERM_COLOR:
                text = colored(text, 'red')

            # print
            self.__print(text)

            # kill
            os._exit(-1)

        """
        This function is called by the manager to show the progress in the output
        """
        def __print_progress(self, total, remaining):

            # generate numbers
            processed = total - remaining
            percent = (processed / float(total)) * 100.00
            percent = int(round(percent, 0))

            # format the output string
            text = "{0:d}% ({1:d} of {2:d})".format(percent, processed, total)
            if USE_TERM_COLOR:
                text = colored(text, 'green')

            # print
            self.__print(text)

        """
        This function is used to print a message to the output in a thread safe manner
        """
        def __print(self, *args, **kwargs):
            self._printLock.acquire(True)
            print(*args, **kwargs)
            self._printLock.release()
