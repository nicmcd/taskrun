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


class FailureModesTestCase(unittest.TestCase):
  def test_aggressive_fail(self):
    self.assertIs(taskrun.FailureMode.create(
      taskrun.FailureMode.AGGRESSIVE_FAIL),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('aggressive_fail'),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('AGGRESSIVE_FAIL'),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('aggrESSIVE_fail'),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create(1),
                  taskrun.FailureMode.AGGRESSIVE_FAIL)

  def test_passive_fail(self):
    self.assertIs(taskrun.FailureMode.create(
      taskrun.FailureMode.PASSIVE_FAIL),
                  taskrun.FailureMode.PASSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('passive_fail'),
                  taskrun.FailureMode.PASSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('PASSIVE_FAIL'),
                  taskrun.FailureMode.PASSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create('pasSIVE_fail'),
                  taskrun.FailureMode.PASSIVE_FAIL)
    self.assertIs(taskrun.FailureMode.create(2),
                  taskrun.FailureMode.PASSIVE_FAIL)

  def test_active_continue(self):
    self.assertIs(taskrun.FailureMode.create(
      taskrun.FailureMode.ACTIVE_CONTINUE),
                  taskrun.FailureMode.ACTIVE_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('active_continue'),
                  taskrun.FailureMode.ACTIVE_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('ACTIVE_CONTINUE'),
                  taskrun.FailureMode.ACTIVE_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('actIVE_continue'),
                  taskrun.FailureMode.ACTIVE_CONTINUE)
    self.assertIs(taskrun.FailureMode.create(3),
                  taskrun.FailureMode.ACTIVE_CONTINUE)

  def test_blind_continue(self):
    self.assertIs(taskrun.FailureMode.create(
      taskrun.FailureMode.BLIND_CONTINUE),
                  taskrun.FailureMode.BLIND_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('blind_continue'),
                  taskrun.FailureMode.BLIND_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('BLIND_CONTINUE'),
                  taskrun.FailureMode.BLIND_CONTINUE)
    self.assertIs(taskrun.FailureMode.create('bliND_continue'),
                  taskrun.FailureMode.BLIND_CONTINUE)
    self.assertIs(taskrun.FailureMode.create(4),
                  taskrun.FailureMode.BLIND_CONTINUE)

  def test_invalid(self):
    with self.assertRaises(ValueError):
      taskrun.FailureMode.create(0)
    with self.assertRaises(ValueError):
      taskrun.FailureMode.create(5)
    with self.assertRaises(ValueError):
      taskrun.FailureMode.create('duh')
    with self.assertRaises(TypeError):
      taskrun.FailureMode.create(float(10))
