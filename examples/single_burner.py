#!/usr/bin/env python3

import os
import taskrun
import tempfile

burncycles = './test/testprogs/burncycles'
if not os.path.exists(burncycles):
  print('"{}" does not exist'.format(burncycles))
  print('you need to run "make burncycles" inside test/testprogs/')
  exit(-1)

loc = tempfile.mkdtemp(prefix='single_burner_')

vob = taskrun.VerboseObserver()
fm = taskrun.FailureMode.AGGRESSIVE_FAIL
tm = taskrun.TaskManager(observers=[vob], failure_mode=fm)

task_name = 't1'
task_cmd = '{} 16 0.1'.format(burncycles)
task = taskrun.ProcessTask(tm, task_name, task_cmd)
task.stdout_file = os.path.join(loc, task_name + '.stdout')
task.stderr_file = os.path.join(loc, task_name + '.stderr')

tm.run_tasks()

print('\nresults at {}'.format(loc))
