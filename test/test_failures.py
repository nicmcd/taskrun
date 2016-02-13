# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .OrderCheckObserver import OrderCheckObserver
from .ComparisonCheckObserver import ComparisonCheckObserver
import os
import unittest
import taskrun


class FailuresTestCase(unittest.TestCase):
  def test_aggressive_none(self):
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='aggressive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'true')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_passive_none(self):
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='passive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'true')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_active_none(self):
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='active_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'true')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_blind_none(self):
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='blind_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'true')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_aggressive_single(self):
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='aggressive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_passive_single(self):
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='passive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_active_single(self):
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='active_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_blind_single(self):
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='blind_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_aggressive_sequence(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t1', '!t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='aggressive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    t2 = taskrun.ProcessTask(tm, 't2', 'false')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_passive_sequence(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t1', '!t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='passive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    t2 = taskrun.ProcessTask(tm, 't2', 'false')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_active_sequence(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t1', '!t1'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='active_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    t2 = taskrun.ProcessTask(tm, 't2', 'false')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_blind_sequence(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t1', '!t1', '+t2', '!t2'])
    tm = taskrun.TaskManager(observer=ob, failure_mode='blind_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    t2 = taskrun.ProcessTask(tm, 't2', 'false')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_aggressive_4wide(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 !t3 !t4 !t2 !t1',
                                  '+t2 > +t1',
                                  '+t2 < +t3 +t4 !t3 !t4 !t2 !t1',
                                  '+t3 > +t2 +t1',
                                  '+t3 < +t4 !t3 !t4 !t2 !t1',
                                  '+t4 > +t3 +t2 +t1',
                                  '+t4 < !t3 !t4 !t2 !t1',
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  '!t3 < !t4 !t2 !t1',
                                  '!t4 > !t3 +t4 +t3 +t2 +t1',
                                  '!t2 > !t3 +t4 +t3 +t2 +t1',
                                  '!t1 > !t3 +t4 +t3 +t2 +t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(observer=ob, failure_mode='aggressive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.04')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.03')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01; false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.02')
    t4.priority = 1
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_passive_4wide(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t2 > +t1',
                                  '+t2 < +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t3 > +t2 +t1',
                                  '+t3 < +t4 !t3 -t4 -t2 -t1',
                                  '+t4 > +t3 +t2 +t1',
                                  '+t4 < !t3 -t4 -t2 -t1',
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  '!t3 < -t4 -t2 -t1',
                                  '-t4 > !t3 +t4 +t3 +t2 +t1',
                                  '-t2 > !t3 +t4 +t3 +t2 +t1',
                                  '-t1 > !t3 +t4 +t3 +t2 +t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(observer=ob, failure_mode='passive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.04')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.03')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01; false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.02')
    t4.priority = 1
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_active_4wide(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t2 > +t1',
                                  '+t2 < +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t3 > +t2 +t1',
                                  '+t3 < +t4 !t3 -t4 -t2 -t1',
                                  '+t4 > +t3 +t2 +t1',
                                  '+t4 < !t3 -t4 -t2 -t1',
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  '-t4 > +t4 +t3 +t2 +t1',
                                  '-t2 > +t4 +t3 +t2 +t1',
                                  '-t1 > +t4 +t3 +t2 +t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(observer=ob, failure_mode='active_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.04')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.03')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01; false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.02')
    t4.priority = 1
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_blind_4wide(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t2 > +t1',
                                  '+t2 < +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t3 > +t2 +t1',
                                  '+t3 < +t4 !t3 -t4 -t2 -t1',
                                  '+t4 > +t3 +t2 +t1',
                                  '+t4 < !t3 -t4 -t2 -t1',
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  '!t3 < -t4 -t2 -t1',
                                  '-t4 > !t3 +t4 +t3 +t2 +t1',
                                  '-t2 > !t3 +t4 +t3 +t2 +t1',
                                  '-t1 > !t3 +t4 +t3 +t2 +t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(observer=ob, failure_mode='blind_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.04')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.03')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01; false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.02')
    t4.priority = 1
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_aggressive_multiroottree_wide(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 !t3 !t4 !t2 !t1',
                                  '+t2 > +t1',
                                  '+t2 < +t3 +t4 !t3 !t4 !t2 !t1',
                                  '+t3 > +t2 +t1',
                                  '+t3 < +t4 !t3 !t4 !t2 !t1',
                                  '+t4 > +t3 +t2 +t1',
                                  '+t4 < !t3 !t4 !t2 !t1',
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  '!t3 < !t4 !t2 !t1',
                                  '!t4 > !t3 +t4 +t3 +t2 +t1',
                                  '!t2 > !t3 +t4 +t3 +t2 +t1',
                                  '!t1 > !t3 +t4 +t3 +t2 +t1'],
                                 verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1000))
    tm = taskrun.TaskManager(observer=ob, resource_manager=rm,
                             failure_mode='aggressive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.04')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.03')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01; false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.02')
    t4.priority = 1
    t3a = taskrun.ProcessTask(tm, 't3a', '')
    t3a.add_dependency(t3)
    t3b = taskrun.ProcessTask(tm, 't3b', '')
    t3b.add_dependency(t3)
    t3ba = taskrun.ProcessTask(tm, 't3ba', '')
    t3ba.add_dependency(t3b)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_passive_multiroottree_wide(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t2 > +t1',
                                  '+t2 < +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t3 > +t2 +t1',
                                  '+t3 < +t4 !t3 -t4 -t2 -t1',
                                  '+t4 > +t3 +t2 +t1',
                                  '+t4 < !t3 -t4 -t2 -t1',
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  '!t3 < -t4 -t2 -t1',
                                  '-t4 > !t3 +t4 +t3 +t2 +t1',
                                  '-t2 > !t3 +t4 +t3 +t2 +t1',
                                  '-t1 > !t3 +t4 +t3 +t2 +t1'],
                                 verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1000))
    tm = taskrun.TaskManager(observer=ob, resource_manager=rm,
                             failure_mode='passive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.04')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.03')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01; false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.02')
    t4.priority = 1
    t3a = taskrun.ProcessTask(tm, 't3a', '')
    t3a.add_dependency(t3)
    t3b = taskrun.ProcessTask(tm, 't3b', '')
    t3b.add_dependency(t3)
    t3ba = taskrun.ProcessTask(tm, 't3ba', '')
    t3ba.add_dependency(t3b)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_active_multiroottree_wide(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t2 > +t1',
                                  '+t2 < +t3 +t4 !t3 -t4 -t2 -t1',
                                  '+t3 > +t2 +t1',
                                  '+t3 < +t4 !t3 -t4 -t2 -t1',
                                  '+t4 > +t3 +t2 +t1',
                                  '+t4 < !t3 -t4 -t2 -t1',
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  '!t3 < -t4 -t2 -t1',
                                  '-t4 > !t3 +t4 +t3 +t2 +t1',
                                  '-t2 > !t3 +t4 +t3 +t2 +t1',
                                  '-t1 > !t3 +t4 +t3 +t2 +t1'],
                                 verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1000))
    tm = taskrun.TaskManager(observer=ob, resource_manager=rm,
                             failure_mode='active_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.04')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.03')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01; false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.02')
    t4.priority = 1
    t3a = taskrun.ProcessTask(tm, 't3a', '')
    t3a.add_dependency(t3)
    t3b = taskrun.ProcessTask(tm, 't3b', '')
    t3b.add_dependency(t3)
    t3ba = taskrun.ProcessTask(tm, 't3ba', '')
    t3ba.add_dependency(t3b)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_blind_multiroottree_wide(self):
    ob = ComparisonCheckObserver(14,
                                 [('+t1 < +t2 +t3 +t4 !t3 +t3a +t3b -t3a -t3b '
                                   '+t3ba -t3ba -t4 -t2 -t1'),
                                  '+t2 > +t1',
                                  ('+t2 < +t3 +t4 !t3 +t3a +t3b -t3a -t3b '
                                   '+t3ba -t3ba -t4 -t2 -t1'),
                                  '+t3 > +t2 +t1',
                                  ('+t3 < +t4 !t3 +t3a +t3b -t3a -t3b '
                                   '+t3ba -t3ba -t4 -t2 -t1'),
                                  '+t4 > +t3 +t2 +t1',
                                  ('+t4 < !t3 +t3a +t3b -t3a -t3b '
                                   '+t3ba -t3ba -t4 -t2 -t1'),
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  ('!t3 < +t3a +t3b -t3a -t3b '
                                   '+t3ba -t3ba -t4 -t2 -t1'),
                                  '+t3a > !t3',
                                  '+t3a < -t3a',
                                  '+t3b > !t3',
                                  '+t3b < -t3b +t3ba -t3ba',
                                  '-t3a > +t3a !t3',
                                  '-t3b > +t3b !t3',
                                  '-t3b < +t3ba -t3ba',
                                  '+t3ba > -t3b +t3b !t3',
                                  '+t3ba < -t3ba',
                                  '-t3ba > +t3ba -t3b +t3b !t3',
                                  '-t4 > !t3 +t4 +t3 +t2 +t1',
                                  '-t2 > !t3 +t4 +t3 +t2 +t1',
                                  '-t1 > !t3 +t4 +t3 +t2 +t1'],
                                 verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1000))
    tm = taskrun.TaskManager(observer=ob, resource_manager=rm,
                             failure_mode='blind_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.04')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.03')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01; false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.02')
    t4.priority = 1
    t3a = taskrun.ProcessTask(tm, 't3a', '')
    t3a.add_dependency(t3)
    t3b = taskrun.ProcessTask(tm, 't3b', '')
    t3b.add_dependency(t3)
    t3ba = taskrun.ProcessTask(tm, 't3ba', '')
    t3ba.add_dependency(t3b)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_aggressive_multiroottree_narrow(self):
    ob = ComparisonCheckObserver(6,
                                 ['+t1 < -t1 +t2 -t2 +t3 !t3',
                                  '-t1 > +t1',
                                  '-t1 < +t2 -t2 +t3 !t3',
                                  '+t2 > -t1 +t1',
                                  '+t2 < -t2 +t3 !t3',
                                  '-t2 > +t2 -t1 +t1',
                                  '-t2 < +t3 !t3',
                                  '+t3 > -t2 +t2 -t1 +t1',
                                  '+t3 < !t3',
                                  '!t3 > +t3 -t2 +t2 -t1 +t1'],
                                 verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    tm = taskrun.TaskManager(observer=ob, resource_manager=rm,
                             failure_mode='aggressive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', '')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', '')
    t4.priority = 1
    t3a = taskrun.ProcessTask(tm, 't3a', '')
    t3a.add_dependency(t3)
    t3b = taskrun.ProcessTask(tm, 't3b', '')
    t3b.add_dependency(t3)
    t3ba = taskrun.ProcessTask(tm, 't3ba', '')
    t3ba.add_dependency(t3b)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_passive_multiroottree_narrow(self):
    ob = ComparisonCheckObserver(6,
                                 ['+t1 < -t1 +t2 -t2 +t3 !t3',
                                  '-t1 > +t1',
                                  '-t1 < +t2 -t2 +t3 !t3',
                                  '+t2 > -t1 +t1',
                                  '+t2 < -t2 +t3 !t3',
                                  '-t2 > +t2 -t1 +t1',
                                  '-t2 < +t3 !t3',
                                  '+t3 > -t2 +t2 -t1 +t1',
                                  '+t3 < !t3',
                                  '!t3 > +t3 -t2 +t2 -t1 +t1'],
                                 verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    tm = taskrun.TaskManager(observer=ob, resource_manager=rm,
                             failure_mode='passive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', '')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', '')
    t4.priority = 1
    t3a = taskrun.ProcessTask(tm, 't3a', '')
    t3a.add_dependency(t3)
    t3b = taskrun.ProcessTask(tm, 't3b', '')
    t3b.add_dependency(t3)
    t3ba = taskrun.ProcessTask(tm, 't3ba', '')
    t3ba.add_dependency(t3b)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_active_multiroottree_narrow(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < -t1 +t2 -t2 +t3 !t3 +t4 -t4',
                                  '-t1 > +t1',
                                  '-t1 < +t2 -t2 +t3 !t3 +t4 -t4',
                                  '+t2 > -t1 +t1',
                                  '+t2 < -t2 +t3 !t3 +t4 -t4',
                                  '-t2 > +t2 -t1 +t1',
                                  '-t2 < +t3 !t3 +t4 -t4',
                                  '+t3 > -t2 +t2 -t1 +t1',
                                  '+t3 < !t3 +t4 -t4',
                                  '!t3 > +t3 -t2 +t2 -t1 +t1',
                                  '!t3 < +t4 -t4',
                                  '+t4 > !t3 +t3 -t2 +t2 -t1 +t1',
                                  '+t4 < -t4',
                                  '-t4 > +t4 !t3 +t3 -t2 +t2 -t1 +t1'],
                                 verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    tm = taskrun.TaskManager(observer=ob, resource_manager=rm,
                             failure_mode='active_continue')
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', '')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', '')
    t4.priority = 1
    t3a = taskrun.ProcessTask(tm, 't3a', '')
    t3a.add_dependency(t3)
    t3b = taskrun.ProcessTask(tm, 't3b', '')
    t3b.add_dependency(t3)
    t3ba = taskrun.ProcessTask(tm, 't3ba', '')
    t3ba.add_dependency(t3b)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_blind_multiroottree_narrow(self):
    ob = ComparisonCheckObserver(14,
                                 [('+t1 < -t1 +t2 -t2 +t3 !t3 +t4 -t4 +t3a '
                                   '-t3a +t3b -t3b +t3ba -t3ba'),
                                  '-t1 > +t1',
                                  ('-t1 < +t2 -t2 +t3 !t3 +t4 -t4 +t3a '
                                   '-t3a +t3b -t3b +t3ba -t3ba'),
                                  '+t2 > -t1 +t1',
                                  ('+t2 < -t2 +t3 !t3 +t4 -t4 +t3a '
                                   '-t3a +t3b -t3b +t3ba -t3ba'),
                                  '-t2 > +t2 -t1 +t1',
                                  ('-t2 < +t3 !t3 +t4 -t4 +t3a '
                                   '-t3a +t3b -t3b +t3ba -t3ba'),
                                  '+t3 > -t2 +t2 -t1 +t1',
                                  ('+t3 < !t3 +t4 -t4 +t3a '
                                   '-t3a +t3b -t3b +t3ba -t3ba'),
                                  '!t3 > +t3 -t2 +t2 -t1 +t1',
                                  ('!t3 < +t4 -t4 +t3a '
                                   '-t3a +t3b -t3b +t3ba -t3ba'),
                                  '+t4 > !t3 +t3 -t2 +t2 -t1 +t1',
                                  ('+t4 < -t4 +t3a '
                                   '-t3a +t3b -t3b +t3ba -t3ba'),
                                  '-t4 > +t4 !t3 +t3 -t2 +t2 -t1 +t1',
                                  '-t4 < +t3a -t3a +t3b -t3b +t3ba -t3ba',
                                  '+t3a > -t4 +t4 !t3 +t3 -t2 +t2 -t1 +t1',
                                  '+t3a < -t3a',
                                  '+t3b > -t4 +t4 !t3 +t3 -t2 +t2 -t1 +t1',
                                  '+t3b < -t3b +t3ba -t3ba',
                                  '-t3a > +t3a -t4 +t4 !t3 +t3 -t2 +t2 -t1 +t1',
                                  '-t3b > +t3b -t4 +t4 !t3 +t3 -t2 +t2 -t1 +t1',
                                  '-t3b < +t3ba -t3ba',
                                  ('+t3ba > -t3b +t3b -t4 +t4 !t3 +t3 -t2 +t2 '
                                   '-t1 +t1'),
                                  '+t3ba < -t3ba',
                                  ('-t3ba > +t3ba -t3b +t3b -t4 +t4 !t3 +t3 '
                                   '-t2 +t2 -t1 +t1')],
                                 verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    tm = taskrun.TaskManager(observer=ob, resource_manager=rm,
                             failure_mode='blind_continue')
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t1.priority = 4
    t2 = taskrun.ProcessTask(tm, 't2', '')
    t2.priority = 3
    t3 = taskrun.ProcessTask(tm, 't3', 'false')
    t3.priority = 2
    t4 = taskrun.ProcessTask(tm, 't4', '')
    t4.priority = 1
    t3a = taskrun.ProcessTask(tm, 't3a', '')
    t3a.add_dependency(t3)
    t3b = taskrun.ProcessTask(tm, 't3b', '')
    t3b.add_dependency(t3)
    t3ba = taskrun.ProcessTask(tm, 't3ba', '')
    t3ba.add_dependency(t3b)
    tm.run_tasks()
    self.assertTrue(ob.ok())
