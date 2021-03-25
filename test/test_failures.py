"""
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""
import os
import unittest
import taskrun
import time
from .OrderCheckObserver import OrderCheckObserver
from .ComparisonCheckObserver import ComparisonCheckObserver


class FailuresTestCase(unittest.TestCase):
  def test_aggressive_none(self):
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='aggressive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'true')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_passive_none(self):
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='passive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'true')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_active_none(self):
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='active_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'true')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_blind_none(self):
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='blind_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'true')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_aggressive_single(self):
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='aggressive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_passive_single(self):
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='passive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_active_single(self):
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='active_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_blind_single(self):
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='blind_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_aggressive_sequence(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t1', '!t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='aggressive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    t2 = taskrun.ProcessTask(tm, 't2', 'false')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_passive_sequence(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t1', '!t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='passive_fail')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    t2 = taskrun.ProcessTask(tm, 't2', 'false')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_active_sequence(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t1', '!t1'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='active_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    t2 = taskrun.ProcessTask(tm, 't2', 'false')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_blind_sequence(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t1', '!t1', '+t2', '!t2'])
    tm = taskrun.TaskManager(observers=[ob], failure_mode='blind_continue')
    t1 = taskrun.ProcessTask(tm, 't1', 'false')
    t2 = taskrun.ProcessTask(tm, 't2', 'false')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_aggressive_4wide(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 !t3 $t4 $t2 $t1',
                                  '+t2 > +t1',
                                  '+t2 < +t3 +t4 !t3 $t4 $t2 $t1',
                                  '+t3 > +t2 +t1',
                                  '+t3 < +t4 !t3 $t4 $t2 $t1',
                                  '+t4 > +t3 +t2 +t1',
                                  '+t4 < !t3 $t4 $t2 $t1',
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  '!t3 < $t4 $t2 $t1',
                                  '$t4 > !t3 +t4 +t3 +t2 +t1',
                                  '$t2 > !t3 +t4 +t3 +t2 +t1',
                                  '$t1 > !t3 +t4 +t3 +t2 +t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(observers=[ob], failure_mode='aggressive_fail')
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
    tm = taskrun.TaskManager(observers=[ob], failure_mode='passive_fail')
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
    tm = taskrun.TaskManager(observers=[ob], failure_mode='active_continue')
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
    tm = taskrun.TaskManager(observers=[ob], failure_mode='blind_continue')
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
                                 ['+t1 < +t2 +t3 +t4 !t3 $t4 $t2 $t1',
                                  '+t2 > +t1',
                                  '+t2 < +t3 +t4 !t3 $t4 $t2 $t1',
                                  '+t3 > +t2 +t1',
                                  '+t3 < +t4 !t3 $t4 $t2 $t1',
                                  '+t4 > +t3 +t2 +t1',
                                  '+t4 < !t3 $t4 $t2 $t1',
                                  '!t3 > +t4 +t3 +t2 +t1',
                                  '!t3 < $t4 $t2 $t1',
                                  '$t4 > !t3 +t4 +t3 +t2 +t1',
                                  '$t2 > !t3 +t4 +t3 +t2 +t1',
                                  '$t1 > !t3 +t4 +t3 +t2 +t1'],
                                 verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1000))
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
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
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
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
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
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
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
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
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
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
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
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
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
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
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
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

  def make_graph(self, tm):
    """
                                   +----+
                                   |    |
                             +---> | t4 |
                             |     |    |
                             |     +----+
                   +----+    |
                   |    | +--+
              +--> | t2 |
    +----+    |    |    | +--+     +----+      +----+
    |    | +--+    +----+    +---> |    |      |    |
    | t1 |                         | t5 | +--> | t6 |
    |    | +--+              +---> |    |      |    |
    +----+    |    +----+    |     +----+      +----+
              |    |    |    |
              +--> | t3 | +--+
                   |    |
                   +----+
    """
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.1')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.3')
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.1; false')
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.1')
    t5 = taskrun.ProcessTask(tm, 't5', 'sleep 0.1')
    t6 = taskrun.ProcessTask(tm, 't6', 'sleep 0.1')
    t6.add_dependency(t5)
    t5.add_dependency(t2)
    t5.add_dependency(t3)
    t4.add_dependency(t2)
    t3.add_dependency(t1)
    t2.add_dependency(t1)

  def test_graph_active(self):
    ob = OrderCheckObserver(
      ['@t1', '@t2', '@t3', '@t4', '@t5', '@t6',
       '+t1', '-t1', '+t3', '+t2', '!t3', '-t2', '+t4', '-t4'],
      verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 2))
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
                             failure_mode='active_continue')
    self.make_graph(tm)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_graph_passive(self):
    ob = OrderCheckObserver(
      ['@t1', '@t2', '@t3', '@t4', '@t5', '@t6',
       '+t1', '-t1', '+t3', '+t2', '!t3', '-t2'],
      verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 2))
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
                             failure_mode='passive_fail')
    self.make_graph(tm)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_graph_aggressive(self):
    ob = OrderCheckObserver(
      ['@t1', '@t2', '@t3', '@t4', '@t5', '@t6',
       '+t1', '-t1', '+t3', '+t2', '!t3', '$t2'],
      verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 2))
    tm = taskrun.TaskManager(observers=[ob], resource_manager=rm,
                             failure_mode='aggressive_fail')
    self.make_graph(tm)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_exception(self):
    for mode in ['aggressive_fail', 'passive_fail', 'active_continue',
                 'blind_continue']:
      for fork in [False, True]:
        ob = OrderCheckObserver(['@t1', '+t1', '!t1'], verbose=False)
        tm = taskrun.TaskManager(observers=[ob], failure_mode=mode)
        t1 = taskrun.FunctionTask(tm, 't1', fork, lambda: 1/0)
        tm.run_tasks()
        self.assertTrue(ob.ok())

  def test_kill_race(self):
    rm = taskrun.ResourceManager(taskrun.CounterResource('slots', 1, 200))
    fm = taskrun.FailureMode.AGGRESSIVE_FAIL
    tm = taskrun.TaskManager(resource_manager=rm, failure_mode=fm)

    taskrun.ProcessTask(tm, 'tfail', 'sleep 0.01; false')
    for tid in range(1000):
      taskrun.ProcessTask(tm, 't' + str(tid), 'sleep 1')

    start_time = time.time()
    tm.run_tasks()
    end_time = time.time()

    # Make sure we actually killed everything and exited quickly. This means
    # taskrun didn't leave tasks running that should have been killed.
    self.assertLess(end_time - start_time, 0.5)
