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
from .ComparisonCheckObserver import ComparisonCheckObserver
from .OrderCheckObserver import OrderCheckObserver


def myfunc(name, number):
  assert isinstance(name, str)
  assert name == 'jimbo'
  assert isinstance(number, int)
  assert number == 5


class CpuTimeResourcesTestCase(unittest.TestCase):
  def test_cputime1(self):
    rm = taskrun.ResourceManager(
      taskrun.CpuTimeResource('time', 1))
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t1.resources = {'time': 1}
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_cputime2(self):
    rm = taskrun.ResourceManager(
      taskrun.CpuTimeResource('time', 10))
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.ProcessTask(
      tm, 't1', 'test/testprogs/burncycles 1 0.1')
    t1.resources = {'time': 10}
    tm.run_tasks()
    self.assertTrue(t1.stdout.find('count=10') >= 0)
    self.assertTrue(t1.stdout.find('completed') >= 0)
    self.assertTrue(ob.ok())

  def test_cputime3(self):
    rm = taskrun.ResourceManager(
      taskrun.CpuTimeResource('time', 20))
    ob = OrderCheckObserver(['@t1', '+t1', '!t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.ProcessTask(
      tm, 't1', 'test/testprogs/burncycles 3.0 0.5')
    t1.resources = {'time': 2}
    tm.run_tasks()
    self.assertTrue(t1.stdout.find('count=1') >= 0)
    self.assertTrue(t1.stdout.find('count=2') >= 0)
    self.assertTrue(t1.stdout.find('count=3') >= 0)
    self.assertTrue(t1.stdout.find('count=5') < 0)
    self.assertTrue(t1.stdout.find('completed') < 0)
    self.assertTrue(ob.ok())

  def test_cputime4(self):
    rm = taskrun.ResourceManager(
      taskrun.CpuTimeResource('time', 20))
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.NopTask(tm, 't1')
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_cputime5(self):
    rm = taskrun.ResourceManager(
      taskrun.CpuTimeResource('time', 20))
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])
    t1 = taskrun.FunctionTask(tm, 't1', myfunc, 'jimbo', 5)
    tm.run_tasks()
    self.assertTrue(ob.ok())

  def test_cputime6(self):
    rm = taskrun.ResourceManager(
      taskrun.CpuTimeResource('time', 20))
    tm = taskrun.TaskManager(rm)
    t1 = taskrun.NopTask(tm, 't1')
    t1.resources = {'time': 20}
    error = False
    try:
      tm.run_tasks()
    except AssertionError:
      error = True
    self.assertTrue(error)

  def test_cputime7(self):
    rm = taskrun.ResourceManager(
      taskrun.CpuTimeResource('time', 20))
    tm = taskrun.TaskManager(rm)
    t1 = taskrun.FunctionTask(tm, 't1', myfunc, 'jimbo', 5)
    t1.resources = {'time': 20}
    error = False
    try:
      tm.run_tasks()
    except AssertionError:
      error = True
    self.assertTrue(error)
