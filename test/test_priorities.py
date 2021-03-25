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
from .ComparisonCheckObserver import ComparisonCheckObserver
import unittest
import taskrun


class PrioritiesTestCase(unittest.TestCase):
  def test_pri1(self):
    ob = ComparisonCheckObserver(4,
                                 ['+t1 < -t1 +t2 -t2',
                                  '+t2 < -t2'],
                                 verbose=False)
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.02')
    t1.priority = 2
    t2.priority = 1
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_pri2(self):
    ob = ComparisonCheckObserver(4,
                                 ['+t2 < -t2 +t1 -t1',
                                  '+t1 < -t1'],
                                 verbose=False)
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.02')
    t1.priority = 1
    t2.priority = 2
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_pri3(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t1 < -t1 +t2 -t2 +t3 -t3 +t4 -t4',
                                  '+t2 < -t2 +t3 -t3 +t4 -t4',
                                  '+t3 < -t3 +t4 -t4',
                                  '+t4 < -t4'],
                                 verbose=False)
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.02')
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.03')
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.04')
    t1.priority = 4
    t2.priority = 3
    t3.priority = 2
    t4.priority = 1
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_pri4(self):
    ob = ComparisonCheckObserver(8,
                                 ['+t2 < -t2 +t1 -t1 +t4 -t4 +t3 -t3',
                                  '+t1 < -t1 +t4 -t4 +t3 -t3',
                                  '+t4 < -t4 +t3 -t3',
                                  '+t3 < -t3'],
                                 verbose=False)
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.02')
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.03')
    t4 = taskrun.ProcessTask(tm, 't4', 'sleep 0.04')
    t1.priority = 3
    t2.priority = 4
    t3.priority = 1
    t4.priority = 2
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_pri5(self):
    tm = taskrun.TaskManager(priority_levels=3)
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.02')
    t1.priority = 2
    t2.priority = 1
    success = True
    try:
      tm.run_tasks()
    except AssertionError:
      success = False
    self.assertTrue(success)

  def test_pri6(self):
    tm = taskrun.TaskManager(priority_levels=2)
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.02')
    t1.priority = 2
    t2.priority = 1
    success = True
    try:
      tm.run_tasks()
    except AssertionError:
      success = False
    self.assertFalse(success)
