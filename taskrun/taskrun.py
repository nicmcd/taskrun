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
VERSION = (2, 1, 0)

"""
This defines one task to be executed
Each task has a set of dependencies, which are other tasks
Each task notifies all tasks that are dependent on it upon completion
"""
class Task(threading.Thread):

    """
    Tasks should not be directly instantiated. The user should use the
    manager.new_task() function
    """
    def __init__(self, manager, name, command=None, output_file=None):
        threading.Thread.__init__(self)
        self._manager = manager
        self._name = name
        self._command = command
        self._output_file = output_file
        self._dependencies = []
        self._notifiees = []
        self._run_cmd = True
        self._accessLock = threading.Lock()

    def get_name(self):
        return self._name

    def get_command(self):
        return self._command

    def get_output_file(self):
        return self._output_file

    """
    These functions must be called BEFORE Manager.run_tasks() is called
    """
    def add_dependency(self, task):
        self._dependencies.append(task)
        task.__add_notifiee(self)

    def set_command(self, command):
        self._command = command

    def set_output_file(self, output_file):
        self._output_file

    """
    These functions are only called by the manager
    """
    def __add_notifiee(self, notifiee):
        self._notifiees.append(notifiee)

    def _run_command(self, run):
        self._run_cmd = run

    def _ready_request(self):
        if not self._dependencies: # test for empty
            self._manager._ready_task(self)

    """
    This function is called by dependent tasks when they complete
    """
    def _notify_done(self, task):
        self._dependencies.remove(task)
        if not self._dependencies: # test for empty
            self._manager._ready_task(self)

    """
    This function is called by the threading library after the class's 'Start'
    function is called
    """
    def run(self):
        # inform the manager that this task is now running
        self._manager._notify_running(self)

        # ensure the command has been set
        if not self._command:
            self._manager._errored_task(self, "command was never set")

        # run the command (optionally)
        if self._run_cmd:
            # execute the task command
            if self._output_file is not None:
                ofd = open(self._output_file, 'w')
            else:
                ofd = open('/dev/null', 'w')
            proc = subprocess.Popen(self._command, stdout=ofd, stderr=ofd, \
                                    shell=True)
            # wait for the process to finish
            proc.wait()
            # close the output
            if self._output_file is not None:
                ofd.close()
            # check the return code
            ret = proc.returncode
            if ret != 0:
                self._manager._notify_error(self, ret)

        # inform the manager of task completion
        self._manager._notify_done(self)
        # inform all notifiees of task completion
        for notifiee in self._notifiees:
            notifiee._notify_done(self)


    """
    This nested class manages a group of tasks
    """
    class Manager():

        def __init__(self, numProcs=None, showCommands=True, runTasks=True, \
                     showProgress=True):
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
            self._totalTasks = None

        """
        This is the effective constructor for a task
        It also adds the task to this manager instance
        """
        def new_task(self, name, command=None, output_file=None):
            task = Task(self, name, command, output_file)
            self._tasks.append(task)
            return task

        """
        This is called by a Task when it becomes ready to run
        """
        def _ready_task(self, task):
            self._readyTasks.append(task)

        """
        This function is called by tasks at the beginning of their 'run'
        function
        """
        def _notify_running(self, task):
            # only print the command when 'showCommands' is True
            if self._showCommands:
                # format the output string
                text = "[Starting '" + task.get_name() + "'] " + \
                       task.get_command()
                if task.get_output_file():
                    text += " &> " + task.get_output_file()
                # print
                self.__print(text)
            # show progress
            self.__print_progress()

        """
        This is called by a Task when it has completed execution
        This is only called by tasks that are listed as dependencies
        """
        def _notify_done(self, task):
            self._tasks.remove(task)
            self._runningTasks.remove(task)
            # only print the command when 'showCommands' is True
            if self._showCommands:
                # format the output string
                text = "[Completed '" + task.get_name() + "'] " + \
                       task.get_command()
                if task.get_output_file():
                    text += " &> " + task.get_output_file()
                # print
                self.__print(text)
            # show progress
            self.__print_progress()

        """
        This function is called by a task when an error code is returned from
        the task
        """
        def _notify_error(self, task, code):
            # format the output string
            text = "[" + task.get_name() + "] ERROR: " + task.get_command()
            if task.get_output_file():
                text += " &> " + task.get_output_file()
            if type(code) == int:
                text += "\nReturn: " + str(code)
            else:
                text += "\nMesage: " + code
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
                # tell the tasks to actually run their command (optionally)
                task._run_command(self._runTasks)
                # ask the tasks to report if they are already to run
                # (root tasks)
                task._ready_request()

            # pre-compute some numbers for statistics
            self._totalTasks = len(self._tasks)

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
                started_percent = int(round((started / float(total)) * 100.00, \
                                            0))

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
