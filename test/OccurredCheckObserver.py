import taskrun


class OccurredCheckObserver(taskrun.Observer):

  def __init__(self, events, verbose=False):
    self._expected = set(events)
    self._actual = set()
    self._verbose = verbose
    self._ok = True

  def reinit(self, events):
    self._expected = set(events)

  def next(self, s):
    if self._verbose:
      print(s)
    self._actual.add(s)

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
      print('expected : {0}'.format(self._expected))
      print('actual   : {0}'.format(self._actual))
    if len(self._expected) != len(self._actual):
      return False
    if len(self._expected.symmetric_difference(self._actual)) > 0:
      return False
    return True
