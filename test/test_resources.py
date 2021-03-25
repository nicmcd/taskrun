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
import random
import unittest
import taskrun
from .ComparisonCheckObserver import ComparisonCheckObserver
from .OrderCheckObserver import OrderCheckObserver


class ResourcesTestCase(unittest.TestCase):
  def test_res1(self):
    rm = taskrun.ResourceManager(
      taskrun.CounterResource('core', 9999, 4),
      taskrun.CounterResource('mem', 9999, 8000))
    tm = taskrun.TaskManager(resource_manager=rm)
    t1 = taskrun.ProcessTask(tm, 't1', '')
    with self.assertRaises(ValueError):
      tm.run_tasks()

  def test_res2(self):
    rm = taskrun.ResourceManager(
      taskrun.CounterResource('core', 9999, 4),
      taskrun.CounterResource('mem', 9999, 8000))
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', '')
    t1.resources = {'core': 1, 'mem': 5000}
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_res3(self):
    rm = taskrun.ResourceManager(
      taskrun.CounterResource('core', 9999, 1),
      taskrun.CounterResource('mem', 9999, 8000))
    ob = OrderCheckObserver(['@t1', '@t2', '@t3', '@t4', '+t1', '-t1', '+t2',
                             '-t2', '+t3', '-t3', '+t4', '-t4'])
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
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
      taskrun.CounterResource('core', 9999, 4),
      taskrun.CounterResource('mem', 9999, 8000))
    ob = OrderCheckObserver(['@t1', '@t2', '@t3', '@t4', '+t1', '-t1', '+t2',
                             '-t2', '+t3', '-t3', '+t4', '-t4'])
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
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
      taskrun.CounterResource('core', 9999, 1),
      taskrun.CounterResource('mem', 9999, 8000))
    ob = OrderCheckObserver(['@t1', '@t2', '@t3', '@t4', '+t1', '-t1', '+t2',
                             '-t2', '+t3', '-t3', '+t4', '-t4'])
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
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
      taskrun.CounterResource('core', 9999, 4),
      taskrun.CounterResource('mem', 9999, 8000))
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 -t4 -t3 -t2 -t1',
                                  '+t2 < +t3 +t4 -t4 -t3 -t2 -t1',
                                  '+t3 < +t4 -t4 -t3 -t2 -t1',
                                  '+t4 < -t4 -t3 -t2 -t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
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
    cr = taskrun.CounterResource('core', 9999, 4)
    cm = taskrun.CounterResource('mem', 9999, 8000)
    rm = taskrun.ResourceManager(cr, cm)
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < +t2 +t3 +t4 -t4 -t3 -t2 -t1',
                                  '+t2 < +t3 +t4 -t4 -t3 -t2 -t1',
                                  '+t3 < +t4 -t4 -t3 -t2 -t1',
                                  '+t4 < -t4 -t3 -t2 -t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
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
    self.assertEqual(cr.total, 4)
    self.assertEqual(cr.used, 0)
    self.assertEqual(cm.total, 8000)
    self.assertEqual(cm.used, 0)

  def test_res8(self):
    for div in [1, 2, 3, 10, 25, 50, 100, 187]:
      cr = taskrun.CounterResource('foo', 4.3/div, 4.3)
      rm = taskrun.ResourceManager(cr)
      tm = taskrun.TaskManager(resource_manager=rm)
      rnd = random.Random(12345678)
      for t in range(10000):
        cmd = 'usleep {}'.format(rnd.gauss(1000, 500))
        taskrun.ProcessTask(tm, str(t), cmd)
      tm.run_tasks()
      self.assertEqual(cr.total, 4.3)
      self.assertEqual(cr.used, 0)
