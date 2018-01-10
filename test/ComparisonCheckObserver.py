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

import taskrun
import time


class ComparisonCheckObserver(taskrun.Observer):

  def __init__(self, events, comparisons, verbose=False):
    super(ComparisonCheckObserver, self).__init__()
    self._events = events
    self._comparisons = comparisons
    self._actual = {}
    self._verbose = verbose
    self._counter = 0

  def reinit(self, events, comparisons):
    assert len(self._actual) == 0
    self._events = events
    self._comparisons = comparisons

  def next(self, s):
    if self._verbose:
      print(s)
    assert s not in self._actual
    self._actual[s] = self._counter
    self._counter += 1
    self._events -= 1

  def task_started(self, task):
    self.next('+{0}'.format(task.name))

  def task_bypassed(self, task):
    self.next('*{0}'.format(task.name))

  def task_completed(self, task):
    self.next('-{0}'.format(task.name))

  def task_failed(self, task, errors):
    self.next('!{0}'.format(task.name))

  def ok(self):
    if self._events != 0:
      print('ERROR: events count is {0}'.format(self._events))
      return False
    for comparison in self._comparisons:
      elements = comparison.split()
      assert len(elements) >= 3
      curr = elements[0]
      if curr not in self._actual:
        print('{0} didn\'t occur'.format(curr))
        return False
      comp = elements[1]
      for other in elements[2:]:
        if other not in self._actual:
          print('{0} didn\'t occur'.format(other))
          return False
        if comp == '<':
          if not (self._actual[curr] < self._actual[other]):
            print('failure: {0}'.format(comparison))
            return False
        elif comp == '>':
          if not (self._actual[curr] > self._actual[other]):
            print('failure: {0}'.format(comparison))
            return False
        else:
          assert False
    return True
