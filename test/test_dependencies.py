# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .OrderCheckObserver import OrderCheckObserver
import unittest
import taskrun


class DependenciesTestCase(unittest.TestCase):
  def test_dep1(self):
    ob = OrderCheckObserver(['+t1', '-t1'])
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', '')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_dep2(self):
    ob = OrderCheckObserver(['+t1', '-t1', '+t2', '-t2'])
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.01')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_dep3(self):
    ob = OrderCheckObserver(['+t2', '-t2', '+t1', '-t1'])
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.01')
    t1.add_dependency(t2)
    tm.run_tasks()
    self.assertTrue(ob.ok())
