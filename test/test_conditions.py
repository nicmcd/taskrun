# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .OrderCheckObserver import OrderCheckObserver
import unittest
import taskrun

thres = 0
total = 0

def myfunc(name, quantity):
  global total
  total += quantity

def cond(*args, **kwargs):
  return total < thres

class ConditionsTestCase(unittest.TestCase):
  def test_allexec(self):
    global total
    global thres
    total = 0
    thres = 100
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    ob = OrderCheckObserver('+t1 -t1 +t2 -t2 +t3 -t3 +t4 -t4'.split())
    tm = taskrun.TaskManager(resource_manager=rm, observer=ob)

    t1 = taskrun.FunctionTask(tm, 't1', myfunc, 'jimbo', 5)
    t1.add_condition(taskrun.FunctionCondition(cond))
    t2 = taskrun.FunctionTask(tm, 't2', myfunc, 'gertrude', 6)
    t2.add_condition(taskrun.FunctionCondition(cond))
    t3 = taskrun.FunctionTask(tm, 't3', myfunc, 'sally', 2)
    t3.add_condition(taskrun.FunctionCondition(cond))
    t4 = taskrun.FunctionTask(tm, 't4', myfunc, 'william', 3)
    t4.add_condition(taskrun.FunctionCondition(cond))

    tm.run_tasks()
    self.assertTrue(ob.ok())
    self.assertEqual(total, 16)

  def test_halfexec(self):
    global total
    global thres
    total = 0
    thres = 10
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    ob = OrderCheckObserver('+t1 -t1 +t2 -t2 *t3 *t4'.split())
    tm = taskrun.TaskManager(resource_manager=rm, observer=ob)

    t1 = taskrun.FunctionTask(tm, 't1', myfunc, 'jimbo', 5)
    t1.add_condition(taskrun.FunctionCondition(cond))
    t2 = taskrun.FunctionTask(tm, 't2', myfunc, 'gertrude', 6)
    t2.add_condition(taskrun.FunctionCondition(cond))
    t3 = taskrun.FunctionTask(tm, 't3', myfunc, 'sally', 2)
    t3.add_condition(taskrun.FunctionCondition(cond))
    t4 = taskrun.FunctionTask(tm, 't4', myfunc, 'william', 3)
    t4.add_condition(taskrun.FunctionCondition(cond))

    tm.run_tasks()
    self.assertTrue(ob.ok())
    self.assertEqual(total, 11)

  def test_noexec(self):
    global total
    global thres
    total = 0
    thres = 0
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    ob = OrderCheckObserver('*t1 *t2 *t3 *t4'.split())
    tm = taskrun.TaskManager(resource_manager=rm, observer=ob)

    t1 = taskrun.FunctionTask(tm, 't1', myfunc, 'jimbo', 5)
    t1.add_condition(taskrun.FunctionCondition(cond))
    t2 = taskrun.FunctionTask(tm, 't2', myfunc, 'gertrude', 6)
    t2.add_condition(taskrun.FunctionCondition(cond))
    t3 = taskrun.FunctionTask(tm, 't3', myfunc, 'sally', 2)
    t3.add_condition(taskrun.FunctionCondition(cond))
    t4 = taskrun.FunctionTask(tm, 't4', myfunc, 'william', 3)
    t4.add_condition(taskrun.FunctionCondition(cond))

    tm.run_tasks()
    self.assertTrue(ob.ok())
    self.assertEqual(total, 0)
