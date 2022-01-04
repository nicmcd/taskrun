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
import taskrun
import tempfile
import unittest


class CommonInstantiationTestCase(unittest.TestCase):
  def basic_load_and_run(self, tm):
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.01')
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01')
    tm.run_tasks()

  def test_basic1(self):
    self.basic_load_and_run(taskrun.basic_task_manager())

  def test_basic2(self):
    self.basic_load_and_run(taskrun.basic_task_manager(
      parallelism=2))

  def test_basic3(self):
    self.basic_load_and_run(taskrun.basic_task_manager(
      verbosity=2))

  def test_basic4(self):
    self.basic_load_and_run(taskrun.basic_task_manager(
      cleanup_files=False))

  def test_basic5(self):
    self.basic_load_and_run(taskrun.basic_task_manager(
      failure_mode='active_continue'))

  def standard_load_and_run(self, tm, track_cpus, track_memory):
    t1 = taskrun.ProcessTask(tm, 't1', 'sleep 0.01')
    t1m = {}
    t2 = taskrun.ProcessTask(tm, 't2', 'sleep 0.01')
    t2m = {}
    t3 = taskrun.ProcessTask(tm, 't3', 'sleep 0.01')
    t3m = {}
    if track_cpus:
      t1m['cpus'] = 1
      t2m['cpus'] = 2
      t3m['cpus'] = 3
    if track_memory:
      t1m['mem'] = 3
      t2m['mem'] = 2
      t3m['mem'] = 1
    t1.resources = t1m
    t2.resources = t2m
    t3.resources = t3m
    tm.run_tasks()

  def test_standard1(self):
    self.standard_load_and_run(
      taskrun.standard_task_manager(track_cpus=True, track_memory=True),
      True, True)

  def test_standard2(self):
    self.standard_load_and_run(
      taskrun.standard_task_manager(track_cpus=True, track_memory=False),
      True, False)

  def test_standard3(self):
    self.standard_load_and_run(
      taskrun.standard_task_manager(track_cpus=False, track_memory=True),
      False, True)

  def test_standard4(self):
    self.standard_load_and_run(
      taskrun.standard_task_manager(track_cpus=False, track_memory=False),
      False, False)

  def test_standard5(self):
    self.standard_load_and_run(
      taskrun.standard_task_manager(verbosity=2),
      True, True)

  def test_standard5(self):
    log_file = tempfile.mkstemp()[1]
    self.standard_load_and_run(
      taskrun.standard_task_manager(log_file=log_file),
      True, True)
    self.assertTrue(os.path.exists(log_file))
    os.remove(log_file)

  def test_standard6(self):
    self.standard_load_and_run(
      taskrun.standard_task_manager(cleanup_files=False),
      True, True)

  def test_standard7(self):
    self.standard_load_and_run(
      taskrun.standard_task_manager(failure_mode='passive_fail'),
      True, True)
