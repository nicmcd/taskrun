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
    if self._order:
      if self._order[0] != s:
        self._ok = False
      self._order.remove(self._order[0])
    else:
      self._ok = False

  def task_started(self, task):
    self.next('+{0}'.format(task.name))

  def task_bypassed(self, task):
    self.next('*{0}'.format(task.name))

  def task_completed(self, task):
    self.next('-{0}'.format(task.name))

  def task_failed(self, task, errors):
    self.next('!{0}'.format(task.name))

  def ok(self):
    return self._ok and len(self._order) == 0

  def actual(self):
    return self._actual
