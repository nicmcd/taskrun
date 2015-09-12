# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .ComparisonCheckObserver import ComparisonCheckObserver
from .OrderCheckObserver import OrderCheckObserver
import os
import unittest
import taskrun


class MemoryResourcesTestCase(unittest.TestCase):
  def test_mem1(self):
    rm = taskrun.ResourceManager(
      taskrun.MemoryResource('ram', 9999, 1))
    ob = OrderCheckObserver('+t1 -t1'.split(), verbose=False)
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t1.resources = {'ram': 1}
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_mem2(self):
    rm = taskrun.ResourceManager(
      taskrun.MemoryResource('ram', 9999, 2))
    ob = OrderCheckObserver('+t1 -t1'.split(), verbose=False)
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(
      tm, 't1', 'test/alloclots/alloclots 104857600 1000 10')
    t1.resources = {'ram': 2}
    tm.run_tasks()
    self.assertTrue(t1.stdout.find('+blocks=10') >= 0)
    self.assertTrue(t1.stdout.find('all allocated') >= 0)
    self.assertTrue(ob.ok())

  def test_mem3(self):
    rm = taskrun.ResourceManager(
      taskrun.MemoryResource('ram', 9999, 1))
    ob = OrderCheckObserver('+t1 !t1'.split(), verbose=False)
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(
      tm, 't1', 'test/alloclots/alloclots 104857600 1000 20')
    t1.resources = {'ram': 1}
    tm.run_tasks()
    self.assertTrue(t1.stdout.find('+blocks=9') >= 0)
    self.assertTrue(t1.stdout.find('all allocated') < 0)
    self.assertTrue(ob.ok())

  def test_mem4(self):
    rm = taskrun.ResourceManager(
      taskrun.MemoryResource('ram', 9999, 0.5))
    ob = OrderCheckObserver('+t1 !t1'.split(), verbose=False)
    tm = taskrun.TaskManager(rm, ob)
    t1 = taskrun.ProcessTask(
      tm, 't1', 'test/alloclots/alloclots 104857600 1000 10')
    t1.resources = {'ram': 0.5}
    tm.run_tasks()
    self.assertTrue(t1.stdout.find('+blocks=4') >= 0)
    self.assertTrue(t1.stdout.find('all allocated') < 0)
    self.assertTrue(ob.ok())
