#!/usr/bin/env python3

import taskrun
import time

def myfunc(name, sleep):
  print(name)
  time.sleep(sleep)

rm = taskrun.ResourceManager(
  taskrun.Resource('core', 9999, 4),
  taskrun.Resource('mem', 9999, 8000))
ob = taskrun.Observer(show_starting=True, show_completed=True)
tm = taskrun.TaskManager(rm, ob)

t1 = taskrun.FunctionTask(tm, 'T1', myfunc, 'jimbo', 0.6)
t1.resources = {'core':4, 'mem':8000}

t2 = taskrun.FunctionTask(tm, 'T2', myfunc, 'gertrude', 0.6)
t2.resources = {'core':2, 'mem':8000}

t3 = taskrun.FunctionTask(tm, 'T3', myfunc, 'sally', 0.6)
t3.resources = {'core':1, 'mem':4000}

t4 = taskrun.FunctionTask(tm, 'T4', myfunc, 'bill', 0.2)
t4.resources = {'core':1, 'mem':4000}

# expected +T1 -T1 +T2 -T2 +T3 +T4 -T4 -T3

tm.run_tasks()
