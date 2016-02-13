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
