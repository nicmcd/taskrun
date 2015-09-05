#!/usr/bin/env python3

import multiprocessing
import sys
import time

import taskrun

def func():
  pass

rm = taskrun.ResourceManager()
tm = taskrun.TaskManager(rm, None)

start = time.time()
for idx in range(3000):
  taskrun.ProcessTask(tm, 'Task_{0:04d}'.format(idx), '')
stop = time.time()
elapsed = stop - start
print('setup time: {0}'.format(elapsed))

num = tm.num_tasks()
start = time.time()
tm.run_tasks()
stop = time.time()
elapsed = stop - start
print('ProcessTasks per second = {0:.3f}'
      .format(num / elapsed))

start = time.time()
for idx in range(3000):
  taskrun.FunctionTask(tm, 'Task_{0:04d}'.format(idx), func)
stop = time.time()
elapsed = stop - start
print('setup time: {0}'.format(elapsed))

num = tm.num_tasks()
start = time.time()
tm.run_tasks()
stop = time.time()
elapsed = stop - start
print('FunctionTasks per second = {0:.3f}'
      .format(num / elapsed))
