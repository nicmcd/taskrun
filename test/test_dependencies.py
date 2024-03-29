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
from .OrderCheckObserver import OrderCheckObserver
import unittest
import taskrun


class DependenciesTestCase(unittest.TestCase):
  def test_dep1(self):
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'])
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', '')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_dep2(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t1', '-t1', '+t2', '-t2'])
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.01')
    t2.add_dependency(t1)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_dep3(self):
    ob = OrderCheckObserver(['@t1', '@t2', '+t2', '-t2', '+t1', '-t1'])
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.01')
    t1.add_dependency(t2)
    tm.run_tasks()
    self.assertTrue(ob.ok())
