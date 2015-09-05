#!/usr/bin/env python3

import taskrun

rm = taskrun.ResourceManager()
ob = taskrun.Observer(show_started=True, show_bypassed=True, show_completed=True)
tm = taskrun.TaskManager(rm, ob)

total = 0

def myfunc(name, quantity):
  global total
  total += quantity
  print('{0} -> {1}'.format(name, total))

def cond(*args, **kwargs):
  return total < 10

t1 = taskrun.FunctionTask(tm, 'T1', myfunc, 'jimbo', 5)
t1.add_condition(taskrun.FunctionCondition(cond))

t2 = taskrun.FunctionTask(tm, 'T2', myfunc, 'gertrude', 4)
t2.add_condition(taskrun.FunctionCondition(cond))

t3 = taskrun.FunctionTask(tm, 'T3', myfunc, 'sally', 3)
t3.add_condition(taskrun.FunctionCondition(cond))

t4 = taskrun.FunctionTask(tm, 'T4', myfunc, 'bill', 2)
t4.add_condition(taskrun.FunctionCondition(cond))

tm.run_tasks()
