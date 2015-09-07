# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import unittest
import taskrun


class FailureModesTestCase(unittest.TestCase):
  def test_aggressive_fail(self):
    self.assertIs(taskrun.FailureMode.create(
      taskrun.FailureMode.AGGRESSIVE_FAIL),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('aggressive_fail'),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('AGGRESSIVE_FAIL'),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('aggrESSIVE_fail'),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create(1),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)

  def test_passive_fail(self):
    self.assertIs(taskrun.FailureMode.create(
      taskrun.FailureMode.PASSIVE_FAIL),
                  taskrun.FailureMode.PASSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('passive_fail'),
                  taskrun.FailureMode.PASSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('PASSIVE_FAIL'),
                  taskrun.FailureMode.PASSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('pasSIVE_fail'),
                  taskrun.FailureMode.PASSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create(2),
                  taskrun.FailureMode.PASSIVE_FAIL)

  def test_active_continue(self):
    self.assertIs(taskrun.FailureMode.create(
      taskrun.FailureMode.ACTIVE_CONTINUE),
                  taskrun.FailureMode.ACTIVE_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('active_continue'),
                  taskrun.FailureMode.ACTIVE_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('ACTIVE_CONTINUE'),
                  taskrun.FailureMode.ACTIVE_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('actIVE_continue'),
                  taskrun.FailureMode.ACTIVE_CONTINUE)
    self.assertIs(taskrun.FailureMode.create(3),
                  taskrun.FailureMode.ACTIVE_CONTINUE)

  def test_blind_continue(self):
    self.assertIs(taskrun.FailureMode.create(
      taskrun.FailureMode.BLIND_CONTINUE),
                  taskrun.FailureMode.BLIND_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('blind_continue'),
                  taskrun.FailureMode.BLIND_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('BLIND_CONTINUE'),
                  taskrun.FailureMode.BLIND_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('bliND_continue'),
                  taskrun.FailureMode.BLIND_CONTINUE)
    self.assertIs(taskrun.FailureMode.create(4),
                  taskrun.FailureMode.BLIND_CONTINUE)

  def test_invalid(self):
    with self.assertRaises(ValueError):
      taskrun.FailureMode.create(0)
    with self.assertRaises(ValueError):
      taskrun.FailureMode.create(5)
    with self.assertRaises(ValueError):
      taskrun.FailureMode.create('duh')
    with self.assertRaises(TypeError):
      taskrun.FailureMode.create(float(10))
