# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import unittest
import taskrun


class ConstructTestCase(unittest.TestCase):
  def test_simple_good(self):
    tm = taskrun.TaskManager()
    tm.run_tasks()

  def test_complex_good(self):
    tm = taskrun.TaskManager(
      observer=taskrun.VerboseObserver(),
      resource_manager=taskrun.ResourceManager(
        taskrun.CounterResource('cpu', 10, 64),
        taskrun.CounterResource('mem', 1024*1024*1024, 256*1024*1024*1024),
        taskrun.CounterResource('net', 1000, 10000),
        taskrun.CounterResource('fds', 500, 50000)),
      failure_mode=taskrun.FailureMode.AGGRESSIVE_FAIL)
    tm.run_tasks()

  def test_simple_badfailuremode(self):
    with self.assertRaises(ValueError):
      tm = taskrun.TaskManager(failure_mode='not a failure mode')
    with self.assertRaises(TypeError):
      tm = taskrun.TaskManager(failure_mode=float(0.19))
