"""
 * Copyright (c) 2012-2016, Nic McDonald
 * All rights reserved.
 *
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
 * - Neither the name of prim nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
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
import taskrun


class OrderCheckObserver(taskrun.Observer):

  def __init__(self, order, verbose=False):
    super(OrderCheckObserver, self).__init__()
    self._order = order
    self._ok = True
    self._actual = []
    self._verbose = verbose

  def next(self, s):
    if self._verbose:
      print(s)
    self._actual.append(s)

  def task_added(self, task):
    self.next('@{0}'.format(task.name))

  def task_started(self, task):
    self.next('+{0}'.format(task.name))

  def task_bypassed(self, task):
    self.next('*{0}'.format(task.name))

  def task_completed(self, task):
    self.next('-{0}'.format(task.name))

  def task_failed(self, task, errors):
    self.next('!{0}'.format(task.name))

  def ok(self):
    if self._verbose:
      print('expected : {0}'.format(self._order))
      print('actual   : {0}'.format(self._actual))
    if len(self._order) != len(self._actual):
      return False
    for idx in range(len(self._order)):
      if self._order[idx] != self._actual[idx]:
        return False
    return True

  def actual(self):
    return self._actual
