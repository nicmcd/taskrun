# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import unittest
import taskrun


class CyclicTestCase(unittest.TestCase):
  def test_selfcyclic(self):
    tm = taskrun.TaskManager()
    t1 = taskrun.ProcessTask(tm, 't1', '')
    with self.assertRaises(ValueError):
      t1.add_dependency(t1)

  def test_deepcyclic(self):
    tm = taskrun.TaskManager()
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t2 = taskrun.ProcessTask(tm, 't2', '')
    t3 = taskrun.ProcessTask(tm, 't3', '')
    t4 = taskrun.ProcessTask(tm, 't4', '')
    t5 = taskrun.ProcessTask(tm, 't5', '')
    t1.add_dependency(t2)
    t2.add_dependency(t3)
    t3.add_dependency(t4)
    t4.add_dependency(t5)
    with self.assertRaises(ValueError):
      t5.add_dependency(t1)

  def test_nocycle1(self):
    tm = taskrun.TaskManager()
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t2 = taskrun.ProcessTask(tm, 't2', '')
    t3 = taskrun.ProcessTask(tm, 't3', '')
    t4 = taskrun.ProcessTask(tm, 't4', '')
    t5 = taskrun.ProcessTask(tm, 't5', '')
    t1.add_dependency(t2)
    t2.add_dependency(t3)
    t3.add_dependency(t4)
    t4.add_dependency(t5)
