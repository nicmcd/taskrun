#!/usr/bin/env python3

import multiprocessing
import os
import sys
import time

import taskrun

def func(first, second, *args, **kwargs):
  assert first == 'you'
  assert second == 'me'
  assert len(args) == 1
  assert args[0] == 'yall'
  assert 'mom' in kwargs
  assert kwargs['mom'] == True
  assert 'dad' in kwargs
  assert kwargs['dad'] == False

num = 3000
cpus = os.cpu_count()
assert cpus > 0
rm = taskrun.ResourceManager(taskrun.CounterResource('cpu', 1, cpus))
tm = taskrun.TaskManager(resource_manager=rm)

# Process task
print('\n*** ProcessTask ***')
start = time.clock()
for idx in range(num):
  taskrun.ProcessTask(tm, 'Task_{0:04d}'.format(idx), '')
stop = time.clock()
elapsed = stop - start
print('setup time: {0:.3f}s'.format(elapsed))

start = time.clock()
tm.run_tasks()
stop = time.clock()
elapsed = stop - start
print('tasks per second: {0:.3f}'
      .format(num / elapsed))

# Function task
print('\n*** FunctionTask ***')
start = time.clock()
for idx in range(num):
  taskrun.FunctionTask(tm, 'Task_{0:04d}'.format(idx),
                       func, 'you', 'me', 'yall', mom=True, dad=False)
stop = time.clock()
elapsed = stop - start
print('setup time: {0:.3f}s'.format(elapsed))

start = time.clock()
tm.run_tasks()
stop = time.clock()
elapsed = stop - start
print('tasks per second: {0:.3f}'
      .format(num / elapsed))

# Nop task
print('\n*** NopTask ***')
start = time.clock()
for idx in range(num):
  taskrun.NopTask(tm, 'Task_{0:04d}'.format(idx))
stop = time.clock()
elapsed = stop - start
print('setup time: {0:.3f}s'.format(elapsed))

start = time.clock()
tm.run_tasks()
stop = time.clock()
elapsed = stop - start
print('tasks per second: {0:.3f}'
      .format(num / elapsed))
