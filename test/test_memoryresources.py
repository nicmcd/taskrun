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
from .OrderCheckObserver import OrderCheckObserver
import os
import unittest
import taskrun


class MemoryResourcesTestCase(unittest.TestCase):
  def test_mem1(self):
    rm = taskrun.ResourceManager(
      taskrun.MemoryResource('ram', 9999, 1))
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t1.resources = {'ram': 1}
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_mem2(self):
    rm = taskrun.ResourceManager(
      taskrun.MemoryResource('ram', 9999, 1))
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.ProcessTask(
      tm, 't1', 'test/testprogs/alloclots 104857600 1000 5')
    t1.resources = {'ram': 0.7}
    tm.run_tasks()
    self.assertTrue(t1.stdout.find('+blocks=4') >= 0)
    self.assertTrue(t1.stdout.find('all allocated') >= 0)
    self.assertTrue(ob.ok())

  def test_mem3(self):
    rm = taskrun.ResourceManager(
      taskrun.MemoryResource('ram', 9999, 0.5))
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.ProcessTask(
      tm, 't1', 'test/testprogs/alloclots 104857600 1000 10')
    t1.resources = {'ram': 0.5}
    tm.run_tasks()
    self.assertTrue(t1.stdout.find('+blocks=4') >= 0)
    self.assertTrue(t1.stdout.find('+blocks=6') < 0)
    self.assertTrue(t1.stdout.find('all allocated') < 0)
    self.assertTrue(ob.ok())

  def test_mem4(self):
    rm = taskrun.ResourceManager(
      taskrun.MemoryResource('ram', 9999, 0.75))
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.ProcessTask(
      tm, 't1', 'test/testprogs/alloclots 104857600 1000 10')
    t1.resources = {'ram': 0.75}
    tm.run_tasks()
    self.assertTrue(t1.stdout.find('+blocks=7') >= 0)
    self.assertTrue(t1.stdout.find('+blocks=8') < 0)
    self.assertTrue(t1.stdout.find('all allocated') < 0)
    self.assertTrue(ob.ok())

  def test_mem5(self):
    rm = taskrun.ResourceManager(
      taskrun.MemoryResource('ram', 9999, 0.25))
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.ProcessTask(
      tm, 't1', 'test/testprogs/alloclots 104857600 1000 5')
    t1.resources = {'ram': 0.25}
    tm.run_tasks()
    self.assertTrue(t1.stdout.find('+blocks=2') >= 0)
    self.assertTrue(t1.stdout.find('all allocated') < 0)
    self.assertTrue(ob.ok())
