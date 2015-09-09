import taskrun


class OccurredCheckObserver(taskrun.Observer):

  def __init__(self, events, verbose=False):
    self._events = set(events)
    self._verbose = verbose
    self._ok = True

  def reinit(self, events):
    self._events = set(events)

  def next(self, s):
    if self._verbose:
      print(s)
    if s not in self._events:
      self._ok = False
    else:
      self._events.remove(s)

  def task_started(self, task):
    self.next('+{0}'.format(task.name))

  def task_bypassed(self, task):
    self.next('*{0}'.format(task.name))

  def task_completed(self, task):
    self.next('-{0}'.format(task.name))

  def task_failed(self, task, errors):
    self.next('!{0}'.format(task.name))

  def ok(self):
    if len(self._events) != 0:
      print('ERROR: events count is {0}'.format(len(self._events)))
      return False
    else:
      return self._ok
