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
import random
import unittest
import taskrun
import tempfile
import time


class FileCleanupObserverTestCase(unittest.TestCase):
  def test_successful(self):
    fd, file1 = tempfile.mkstemp()
    fd, file2 = tempfile.mkstemp()
    fd, file3 = tempfile.mkstemp()
    os.remove(file3)

    with open(file1, 'w') as fd:
      print('hello file1', file=fd)
    with open(file2, 'w') as fd:
      print('hello file2', file=fd)
    time.sleep(0.01)

    ob = taskrun.FileCleanupObserver()
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    t1.add_condition(taskrun.FileModificationCondition(
      [file1, file2], [file3]))

    tm.run_tasks()
    self.assertTrue(os.path.isfile(file1))
    self.assertTrue(os.path.isfile(file2))
    self.assertTrue(os.path.isfile(file3))

    # remove all files
    os.remove(file1)
    os.remove(file2)
    os.remove(file3)

  def test_failure(self):
    fd, file1 = tempfile.mkstemp()
    fd, file2 = tempfile.mkstemp()
    fd, file3 = tempfile.mkstemp()
    os.remove(file3)

    with open(file1, 'w') as fd:
      print('hello file1', file=fd)
    with open(file2, 'w') as fd:
      print('hello file2', file=fd)
    time.sleep(0.01)

    ob = taskrun.FileCleanupObserver()
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}; false'
                             .format(file1, file2, file3))
    t1.add_condition(taskrun.FileModificationCondition(
      [file1, file2], [file3]))

    tm.run_tasks()
    self.assertTrue(os.path.isfile(file1))
    self.assertTrue(os.path.isfile(file2))
    self.assertFalse(os.path.isfile(file3))

    # remove all files
    os.remove(file1)
    os.remove(file2)

  def test_nooutputfiles(self):
    fd, file1 = tempfile.mkstemp()
    fd, file2 = tempfile.mkstemp()
    fd, file3 = tempfile.mkstemp()
    os.remove(file3)

    with open(file1, 'w') as fd:
      print('hello file1', file=fd)
    with open(file2, 'w') as fd:
      print('hello file2', file=fd)
    time.sleep(0.01)

    ob = taskrun.FileCleanupObserver()
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'false'
                             .format(file1, file2, file3))
    t1.add_condition(taskrun.FileModificationCondition(
      [file1, file2], [file3]))

    tm.run_tasks()
    self.assertTrue(os.path.isfile(file1))
    self.assertTrue(os.path.isfile(file2))
    self.assertFalse(os.path.isfile(file3))

    # remove all files
    os.remove(file1)
    os.remove(file2)

  def test_noinputfiles(self):
    fd, file1 = tempfile.mkstemp()
    fd, file2 = tempfile.mkstemp()
    fd, file3 = tempfile.mkstemp()
    os.remove(file1)
    os.remove(file2)
    os.remove(file3)

    time.sleep(0.01)

    ob = taskrun.FileCleanupObserver()
    tm = taskrun.TaskManager(observers=[ob])
    t1 = taskrun.ProcessTask(tm, 't1', 'false'
                             .format(file1, file2, file3))
    t1.add_condition(taskrun.FileModificationCondition(
      [file1, file2], [file3]))

    tm.run_tasks()
    self.assertFalse(os.path.isfile(file1))
    self.assertFalse(os.path.isfile(file2))
    self.assertFalse(os.path.isfile(file3))
