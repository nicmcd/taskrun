# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import unittest
import taskrun
import tempfile


class ProcessesTestCase(unittest.TestCase):
  def test_proc1(self):
    fd, filename = tempfile.mkstemp()
    tm = taskrun.TaskManager()
    t1 = taskrun.ProcessTask(tm, 't1', 'rm {0}'.format(filename))
    with open(filename, 'w') as fd:
      print('hello world!\n', file=fd)
    self.assertTrue(os.path.isfile(filename))
    tm.run_tasks()
    self.assertFalse(os.path.isfile(filename))

  def test_proc2(self):
    pass  # needs a good error mode
