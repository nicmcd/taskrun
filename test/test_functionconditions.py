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
import unittest
import taskrun
from .OrderCheckObserver import OrderCheckObserver


thres = 0
total = 0

def myfunc(name, quantity):
  global total
  total += quantity

def cond(*args, **kwargs):
  return total < thres

class FunctionConditionsTestCase(unittest.TestCase):
  def test_allexec(self):
    global total
    global thres
    total = 0
    thres = 100
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    ob = OrderCheckObserver(['@t1', '@t2', '@t3', '@t4', '+t1', '-t1', '+t2',
                             '-t2', '+t3', '-t3', '+t4', '-t4'])
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])

    t1 = taskrun.FunctionTask(tm, 't1', myfunc, 'jimbo', 5)
    t1.add_condition(taskrun.FunctionCondition(cond))
    t2 = taskrun.FunctionTask(tm, 't2', myfunc, 'gertrude', 6)
    t2.add_condition(taskrun.FunctionCondition(cond))
    t3 = taskrun.FunctionTask(tm, 't3', myfunc, 'sally', 2)
    t3.add_condition(taskrun.FunctionCondition(cond))
    t4 = taskrun.FunctionTask(tm, 't4', myfunc, 'william', 3)
    t4.add_condition(taskrun.FunctionCondition(cond))

    tm.run_tasks()
    self.assertTrue(ob.ok())
    self.assertEqual(total, 16)

  def test_halfexec(self):
    global total
    global thres
    total = 0
    thres = 10
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    ob = OrderCheckObserver(['@t1', '@t2', '@t3', '@t4', '+t1', '-t1', '+t2',
                             '-t2', '*t3', '*t4'])
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])

    t1 = taskrun.FunctionTask(tm, 't1', myfunc, 'jimbo', 5)
    t1.add_condition(taskrun.FunctionCondition(cond))
    t2 = taskrun.FunctionTask(tm, 't2', myfunc, 'gertrude', 6)
    t2.add_condition(taskrun.FunctionCondition(cond))
    t3 = taskrun.FunctionTask(tm, 't3', myfunc, 'sally', 2)
    t3.add_condition(taskrun.FunctionCondition(cond))
    t4 = taskrun.FunctionTask(tm, 't4', myfunc, 'william', 3)
    t4.add_condition(taskrun.FunctionCondition(cond))

    tm.run_tasks()
    self.assertTrue(ob.ok())
    self.assertEqual(total, 11)

  def test_noexec(self):
    global total
    global thres
    total = 0
    thres = 0
    rm = taskrun.ResourceManager(taskrun.CounterResource('slot', 1, 1))
    ob = OrderCheckObserver(['@t1', '@t2', '@t3', '@t4', '*t1', '*t2', '*t3',
                             '*t4'])
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])

    t1 = taskrun.FunctionTask(tm, 't1', myfunc, 'jimbo', 5)
    t1.add_condition(taskrun.FunctionCondition(cond))
    t2 = taskrun.FunctionTask(tm, 't2', myfunc, 'gertrude', 6)
    t2.add_condition(taskrun.FunctionCondition(cond))
    t3 = taskrun.FunctionTask(tm, 't3', myfunc, 'sally', 2)
    t3.add_condition(taskrun.FunctionCondition(cond))
    t4 = taskrun.FunctionTask(tm, 't4', myfunc, 'william', 3)
    t4.add_condition(taskrun.FunctionCondition(cond))

    tm.run_tasks()
    self.assertTrue(ob.ok())
    self.assertEqual(total, 0)
