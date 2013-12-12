#!/usr/bin/env python

import sys

try:
    import taskrun
except:
    print("'taskrun' doesn't appear to be installed. Did you install it?")
    print("You can install it locally by running:")
    print("python setup.py install --user")
    sys.exit(-1)

# create a task manager
manager = taskrun.Task.Manager(numProcs=2, showCommands=True, runTasks=True, showProgress=True)

# create some tasks
task1 = manager.task_new("Task1", "cat LICENSE");
task2 = manager.task_new("Task2", "echo world hello!", "fun/output.txt");
task3 = manager.task_new("Task3", "mkdir fun");

# set task dependencies
task1.dependency_is(task2)
task2.dependency_is(task3)

# run all tasks
manager.run_request_is()
