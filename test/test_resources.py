# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .ComparisonCheckObserver import ComparisonCheckObserver
from .OrderCheckObserver import OrderCheckObserver
import unittest
import taskrun


class ResourcesTestCase(unittest.TestCase):
  def test_res1(self):
    rm = taskrun.ResourceManager(
      taskrun.Resource('core', 9999, 4),
      taskrun.Resource('mem', 9999, 8000))
    tm = taskrun.TaskManager(rm, None)
    t1 = taskrun.ProcessTask(tm, 't1', '')
    with self.assertRaises(ValueError):
      tm.run_tasks()

  def test_res2(self):
    rm = taskrun.ResourceManager(
      taskrun.Resource('core', 9999, 4),
      taskrun.Resource('mem', 9999, 8000))
    ob = OrderCheckObserver(['+t1', '-t1'])
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t1.resources = {'core': 1, 'mem': 5000}
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_res3(self):
    rm = taskrun.ResourceManager(
      taskrun.Resource('core', 9999, 1),
      taskrun.Resource('mem', 9999, 8000))
    ob = OrderCheckObserver('+t1 -t1 +t2 -t2 +t3 -t3 +t4 -t4'.split())
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t1.resources = {'core': 1, 'mem': 0}
    t2 = taskrun.ProcessTask(tm, 't2', '')
    t2.resources = {'core': 1, 'mem': 0}
    t3 = taskrun.ProcessTask(tm, 't3', '')
    t3.resources = {'core': 1, 'mem': 0}
    t4 = taskrun.ProcessTask(tm, 't4', '')
    t4.resources = {'core': 1, 'mem': 0}
    t4.add_dependency(t3)
    t3.add_dependency(t2)
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_res4(self):
    rm = taskrun.ResourceManager(
      taskrun.Resource('core', 9999, 4),
      taskrun.Resource('mem', 9999, 8000))
    ob = OrderCheckObserver('+t1 -t1 +t2 -t2 +t3 -t3 +t4 -t4'.split())
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t1.resources = {'core': 1, 'mem': 0}
    t2 = taskrun.ProcessTask(tm, 't2', '')
    t2.resources = {'core': 1, 'mem': 0}
    t3 = taskrun.ProcessTask(tm, 't3', '')
    t3.resources = {'core': 1, 'mem': 0}
    t4 = taskrun.ProcessTask(tm, 't4', '')
    t4.resources = {'core': 1, 'mem': 0}
    t4.add_dependency(t3)
    t3.add_dependency(t2)
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_res5(self):
    rm = taskrun.ResourceManager(
      taskrun.Resource('core', 9999, 1),
      taskrun.Resource('mem', 9999, 8000))
    ob = OrderCheckObserver('+t1 -t1 +t2 -t2 +t3 -t3 +t4 -t4'.split())
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t1.resources = {'core': 1, 'mem': 0}
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', '')
    t2.resources = {'core': 1, 'mem': 0}
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', '')
    t3.resources = {'core': 1, 'mem': 0}
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', '')
    t4.resources = {'core': 1, 'mem': 0}
    t4.priority = 1
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_res6(self):
    rm = taskrun.ResourceManager(
      taskrun.Resource('core', 9999, 4),
      taskrun.Resource('mem', 9999, 8000))
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 -t4 -t3 -t2 -t1',
                                  '+t2 < +t3 +t4 -t4 -t3 -t2 -t1',
                                  '+t3 < +t4 -t4 -t3 -t2 -t1',
                                  '+t4 < -t4 -t3 -t2 -t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.04')
    t1.resources = {'core': 1, 'mem': 0}
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.03')
    t2.resources = {'core': 1, 'mem': 0}
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.02')
    t3.resources = {'core': 1, 'mem': 0}
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.01')
    t4.resources = {'core': 1, 'mem': 0}
    t4.priority = 1
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_res7(self):
    rm = taskrun.ResourceManager(
      taskrun.Resource('core', 9999, 4),
      taskrun.Resource('mem', 9999, 8000))
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 -t4 -t3 -t2 -t1',
                                  '+t2 < +t3 +t4 -t4 -t3 -t2 -t1',
                                  '+t3 < +t4 -t4 -t3 -t2 -t1',
                                  '+t4 < -t4 -t3 -t2 -t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t1.resources = {'core': 1, 'mem': 0}
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.02')
    t2.resources = {'core': 1, 'mem': 0}
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.03')
    t3.resources = {'core': 1, 'mem': 0}
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.04')
    t4.resources = {'core': 1, 'mem': 0}
    t4.priority = 1
    tm.run_tasks()
    self.assertTrue(ob.ok())
