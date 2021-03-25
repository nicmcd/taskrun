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
import os
import unittest
import signal
import subprocess
import taskrun
import threading
import time


def send_signal(pid, sig, sleep):
  if sig:
    cmd = ['kill', '-{}'.format(int(sig)), str(pid)]
  else:
    cmd = ['kill', str(pid)]
  time.sleep(sleep)
  subprocess.run(cmd, check=False)

class SignalTestCase(unittest.TestCase):

  def test_sigint_one_ignored(self):
    ob = OrderCheckObserver(
      ['@t0', '@t1', '@t2', '@t3',
       '+t0', '-t0', '+t1', '-t1', '+t2', '-t2', '+t3', '-t3'],
      verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slots', 1, 1))
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob],
                             failure_mode='blind_continue')
    tasks = []
    for tid in range(4):
      tasks.append(taskrun.ProcessTask(tm, 't{}'.format(tid), 'sleep 0.5'))
    pid = os.getpid()
    threading.Thread(
      target=send_signal, args=(pid, signal.SIGINT, 1.25)).start()
    res = tm.run_tasks()
    self.assertTrue(res)
    self.assertTrue(ob.ok())

  def test_sigint_two_ignored(self):
    ob = OrderCheckObserver(
      ['@t0', '@t1', '@t2', '@t3',
       '+t0', '-t0', '+t1', '-t1', '+t2', '-t2', '+t3', '-t3'],
      verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slots', 1, 1))
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob],
                             failure_mode='blind_continue')
    tasks = []
    for tid in range(4):
      tasks.append(taskrun.ProcessTask(tm, 't{}'.format(tid), 'sleep 1.0'))
    pid = os.getpid()
    threading.Thread(
      target=send_signal, args=(pid, signal.SIGINT, 0.150)).start()
    threading.Thread(
      target=send_signal, args=(pid, signal.SIGINT, 3.550)).start()
    res = tm.run_tasks()
    self.assertTrue(res)
    self.assertTrue(ob.ok())


  def test_sigint_two_accepted(self):
    ob = OrderCheckObserver(
      ['@t0', '@t1', '@t2', '@t3',
       '+t0', '-t0', '+t1', '-t1', '+t2', '$t2',],
      verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slots', 1, 1))
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob],
                             failure_mode='blind_continue')
    tasks = []
    for tid in range(4):
      tasks.append(taskrun.ProcessTask(tm, 't{}'.format(tid), 'sleep 0.5'))
    pid = os.getpid()
    threading.Thread(
      target=send_signal, args=(pid, signal.SIGINT, 0.25)).start()
    threading.Thread(
      target=send_signal, args=(pid, signal.SIGINT, 1.25)).start()
    res = tm.run_tasks()
    self.assertFalse(res)
    self.assertTrue(ob.ok())

  def test_sigterm(self):
    ob = OrderCheckObserver(
      ['@t0', '@t1', '@t2', '@t3',
       '+t0', '-t0', '+t1', '-t1', '+t2', '$t2'],
      verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slots', 1, 1))
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob],
                             failure_mode='blind_continue')
    tasks = []
    for tid in range(4):
      tasks.append(taskrun.ProcessTask(tm, 't{}'.format(tid), 'sleep 0.5'))
    pid = os.getpid()
    threading.Thread(
      target=send_signal, args=(pid, signal.SIGTERM, 1.25)).start()
    res = tm.run_tasks()
    self.assertFalse(res)
    self.assertTrue(ob.ok())

  def test_sigint_sigterm(self):
    ob = OrderCheckObserver(
      ['@t0', '@t1', '@t2', '@t3',
       '+t0', '-t0', '+t1', '-t1', '+t2', '-t2', '+t3', '$t3'],
      verbose=False)
    rm = taskrun.ResourceManager(taskrun.CounterResource('slots', 1, 1))
    tm = taskrun.TaskManager(resource_manager=rm, observers=[ob],
                             failure_mode='blind_continue')
    tasks = []
    for tid in range(4):
      tasks.append(taskrun.ProcessTask(tm, 't{}'.format(tid), 'sleep 1.0'))
    pid = os.getpid()
    threading.Thread(
      target=send_signal, args=(pid, signal.SIGINT, 0.100)).start()
    threading.Thread(
      target=send_signal, args=(pid, signal.SIGTERM, 3.550)).start()
    res = tm.run_tasks()
    self.assertFalse(res)
    self.assertTrue(ob.ok())
