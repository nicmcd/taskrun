# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .OrderCheckObserver import OrderCheckObserver
import os
import unittest
import taskrun
import tempfile



class FileConditionsTestCase(unittest.TestCase):
  def test_simple(self):
    fd, dbpath = tempfile.mkstemp()
    fd, file1 = tempfile.mkstemp()
    fd, file2 = tempfile.mkstemp()
    fd, file3 = tempfile.mkstemp()

    with open(file1, 'w') as fd:
      print('hello file1', file=fd)
    with open(file2, 'w') as fd:
      print('hello file2', file=fd)

    # initial run
    filedb = taskrun.FileChangedDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # nothing changed
    filedb = taskrun.FileChangedDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['*t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # nothing changed
    filedb = taskrun.FileChangedDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['*t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # missing output
    os.remove(file3)
    filedb = taskrun.FileChangedDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # nothing changed
    filedb = taskrun.FileChangedDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['*t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # input changed
    with open(file1, 'w') as fd:
      print('hello file1!', file=fd)
    filedb = taskrun.FileChangedDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # nothing changed
    filedb = taskrun.FileChangedDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['*t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # remove all files
    os.remove(dbpath)
    os.remove(file1)
    os.remove(file2)
    os.remove(file3)
