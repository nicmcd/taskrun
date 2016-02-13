import taskrun
import time


class ComparisonCheckObserver(taskrun.Observer):

  def __init__(self, events, comparisons, verbose=False):
    super(ComparisonCheckObserver, self).__init__()
    self._events = events
    self._comparisons = comparisons
    self._actual = {}
    self._verbose = verbose

  def reinit(self, events, comparisons):
    assert len(self._actual) == 0
    self._events = events
    self._comparisons = comparisons

  def next(self, s):
    if self._verbose:
      print(s)
    assert s not in self._actual
    self._actual[s] = time.clock()
    self._events -= 1

  def task_added(self, task):
    pass

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
          if not self._actual[curr] < self._actual[other]:
            print('failure: {0}'.format(comparison))
            return False
        elif comp == '>':
          if not self._actual[curr] > self._actual[other]:
            print('failure: {0}'.format(comparison))
            return False
        else:
          assert False
    return True
