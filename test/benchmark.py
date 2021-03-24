#!/usr/bin/env python3
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

import os
import subprocess
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
print('Using {} cpus for benchmarking'.format(cpus))
assert cpus > 0

def get_tm():
  rm = taskrun.ResourceManager(taskrun.CounterResource('cpu', 1, cpus))
  tm = taskrun.TaskManager(resource_manager=rm)
  return tm

# Process task
print('\n*** ProcessTask ***')
start = time.time()
tm = get_tm()
for idx in range(num):
  taskrun.ProcessTask(tm, 'Task_{0:04d}'.format(idx), 'true')
stop = time.time()
elapsed = stop - start
print('setup time: {0:.3f}s'.format(elapsed))
start = time.time()
tm.run_tasks()
stop = time.time()
elapsed = stop - start
print('tasks per second: {0:.3f}'
      .format(num / elapsed))

# Function task
print('\n*** FunctionTask ***')
start = time.time()
tm = get_tm()
for idx in range(num):
  taskrun.FunctionTask(tm, 'Task_{0:04d}'.format(idx), False,
                       func, 'you', 'me', 'yall', mom=True, dad=False)
stop = time.time()
elapsed = stop - start
print('setup time: {0:.3f}s'.format(elapsed))
start = time.time()
tm.run_tasks()
stop = time.time()
elapsed = stop - start
print('tasks per second: {0:.3f}'
      .format(num / elapsed))

# Nop task
print('\n*** NopTask ***')
start = time.time()
tm = get_tm()
for idx in range(num):
  taskrun.NopTask(tm, 'Task_{0:04d}'.format(idx))
stop = time.time()
elapsed = stop - start
print('setup time: {0:.3f}s'.format(elapsed))
start = time.time()
tm.run_tasks()
stop = time.time()
elapsed = stop - start
print('tasks per second: {0:.3f}'
      .format(num / elapsed))

# Cluster task
print('\n*** ClusterTask ***')
try:
  subprocess.call('qstat')  # will trigger FileNotFoundError
  gnum = 3

  start = time.time()
  tm = get_tm()
  for idx in range(gnum):
    nm = 'Task_{0:04d}'.format(idx)
    gt = taskrun.ClusterTask(tm, nm, 'touch output_{0}'.format(nm), mode='sge')
  stop = time.time()
  elapsed = stop - start
  print('setup time: {0:.3f}s'.format(elapsed))

  start = time.time()
  tm.run_tasks()
  stop = time.time()
  elapsed = stop - start
  print('tasks per second: {0:.3f}'
        .format(gnum / elapsed))
except FileNotFoundError:
  print('qstat/qsub not installed, not performing ClusterTask benchmark')
