#!/usr/bin/env python3

import os
import taskrun
import tempfile

besleepy = './test/testprogs/besleepy'
if not os.path.exists(besleepy):
  print('"{}" does not exist'.format(besleepy))
  print('you need to run "make besleepy" inside test/testprogs/')
  exit(-1)

loc = tempfile.mkdtemp(prefix='many_sleepers_')

rm = taskrun.ResourceManager(
  taskrun.CounterResource('slots', 1, 200))
vob = taskrun.VerboseObserver()
fm = taskrun.FailureMode.AGGRESSIVE_FAIL
tm = taskrun.TaskManager(resource_manager=rm, observers=[vob], failure_mode=fm)

for tid in range(1000):
  task_name = 't' + str(tid)
  task_cmd = '{} 1 0.1'.format(besleepy)
  task = taskrun.ProcessTask(tm, task_name, task_cmd)
  task.stdout_file = os.path.join(loc, task_name + '.stdout')
  task.stderr_file = os.path.join(loc, task_name + '.stderr')

tm.run_tasks()

print('\nresults at {}'.format(loc))
