#!/usr/bin/env python3

import multiprocessing
import sys

import taskrun

def doit(first, *args, **kwargs):
  print('first:')
  print('  {0}'.format(first))
  print('args:')
  for a in args:
    print('  {0}'.format(a))
  print('kwargs:')
  for k in kwargs:
    print('  {0}->{1}'.format(k, kwargs[k]))

# create a resource manager
rm = taskrun.ResourceManager(
  taskrun.Resource('cpu', 1, multiprocessing.cpu_count()),
  taskrun.Resource('mem', 500, 8000))

# create a task manager
ob = taskrun.Observer(show_starting=True, show_completed=True)
tm = taskrun.TaskManager(rm, ob)

# create some tasks
task1 = taskrun.ProcessTask(tm, "Task1", "cat LICENSE");
task2 = taskrun.ProcessTask(tm, "Task2", "echo \"this is stdout\"; "
                            "echo \"this is stderr\" 1>&2")
task2.stdout = "/tmp/fun/output.txt"
task2.stderr = "/tmp/fun/error.txt"
task3 = taskrun.ProcessTask(tm, "Task3", "mkdir -p /tmp/fun")
task4 = taskrun.FunctionTask(tm, "Task4", doit, 1, 2, 3, age=29, car='BMW')

# set task dependencies
task1.add_dependency(task2)
task2.add_dependency(task3)
task4.add_dependency(task1)
task4.add_dependency(task2)
task4.add_dependency(task3)

# run all tasks
tm.run_tasks()
