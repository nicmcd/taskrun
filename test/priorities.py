#!/usr/bin/env python3

import taskrun
import time

def myfunc(name, sleep):
  print(name)
  time.sleep(sleep)

rm = taskrun.ResourceManager()
ob = taskrun.Observer(show_starting=True, show_completed=True)
tm = taskrun.TaskManager(rm, ob)

t1 = taskrun.FunctionTask(tm, 'T1', myfunc, 'jimbo', 0.1)
t1.priority = 10

t2 = taskrun.FunctionTask(tm, 'T2', myfunc, 'gertrude', 0.4)
t2.priority = 11

t3 = taskrun.FunctionTask(tm, 'T3', myfunc, 'sally', 0.6)
t3.priority = 12

t4 = taskrun.FunctionTask(tm, 'T4', myfunc, 'bill', 0.8)
t4.priority = 13

# expected +T4 +T3 +T2 +T1 -T1 -T2 -T3 -T4

tm.run_tasks()
