#!/usr/bin/env python3

import multiprocessing
import sys
import time

import taskrun

rm = taskrun.ResourceManager()
tm = taskrun.TaskManager(rm, None)

for idx in range(3000):
  taskrun.ProcessTask(tm, 'Task_{0:04d}'.format(idx), '')

num = tm.num_tasks()
start = time.time()
tm.run_tasks()
stop = time.time()
elapsed = stop - start
print('ProcessTasks per second = {0:.3f}'
      .format(num / elapsed))

def func():
  pass

for idx in range(3000):
  taskrun.FunctionTask(tm, 'Task_{0:04d}'.format(idx), func)

num = tm.num_tasks()
start = time.time()
tm.run_tasks()
stop = time.time()
elapsed = stop - start
print('FunctionTasks per second = {0:.3f}'
      .format(num / elapsed))
