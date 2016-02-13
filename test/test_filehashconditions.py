# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .OccurredCheckObserver import OccurredCheckObserver
from .OrderCheckObserver import OrderCheckObserver
import os
import random
import unittest
import taskrun
import tempfile



class FileHashConditionsTestCase(unittest.TestCase):
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
    filedb = taskrun.FileHashDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileHashCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # nothing changed
    filedb = taskrun.FileHashDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['@t1', '*t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileHashCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # nothing changed
    filedb = taskrun.FileHashDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['@t1', '*t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileHashCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # missing output
    os.remove(file3)
    filedb = taskrun.FileHashDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileHashCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # nothing changed
    filedb = taskrun.FileHashDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['@t1', '*t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileHashCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # input changed
    with open(file1, 'w') as fd:
      print('hello file1!', file=fd)
    filedb = taskrun.FileHashDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['@t1', '+t1', '-t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileHashCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # nothing changed
    filedb = taskrun.FileHashDatabase(dbpath, 'sha512')
    ob = OrderCheckObserver(['@t1', '*t1'], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    t1 = taskrun.ProcessTask(tm, 't1', 'cat {0} {1} > {2}'
                             .format(file1, file2, file3))
    c1 = taskrun.FileHashCondition(filedb, [file1, file2], [file3])
    t1.add_condition(c1)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # remove all files
    os.remove(dbpath)
    os.remove(file1)
    os.remove(file2)
    os.remove(file3)

  def test_many(self):
    fd, dbpath = tempfile.mkstemp()

    # create files for processes
    procs = 100
    files = []
    for proc_id in range(procs):
      fd, file_a = tempfile.mkstemp()
      fd, file_b = tempfile.mkstemp()
      fd, file_c = tempfile.mkstemp()
      files.append([file_a, file_b, file_c])

    # write something into A and B files
    for proc_id in range(procs):
      with open(files[proc_id][0], 'w') as afile:
        print('hello file A from proc {0}'.format(proc_id), file=afile)
      with open(files[proc_id][1], 'w') as bfile:
        print('hello file B from proc {0}'.format(proc_id), file=bfile)


    # initial
    filedb = taskrun.FileHashDatabase(dbpath, 'md5')
    ob = OccurredCheckObserver([], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    evts = []
    for proc_id in range(procs):
      task = taskrun.ProcessTask(tm, 't{0:04}'.format(proc_id),
                                 'cat {0} {1} > {2}'.format(
                                   files[proc_id][0], files[proc_id][1],
                                   files[proc_id][2]));
      cond = taskrun.FileHashCondition(filedb,
                                       [files[proc_id][0], files[proc_id][1]],
                                       [files[proc_id][2]])
      task.add_condition(cond)
      evts.append('@{0}'.format(task.name))
      evts.append('+{0}'.format(task.name))
      evts.append('-{0}'.format(task.name))
    ob.reinit(evts)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # no change
    filedb = taskrun.FileHashDatabase(dbpath, 'md5')
    ob = OccurredCheckObserver([], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    evts = []
    for proc_id in range(procs):
      task = taskrun.ProcessTask(tm, 't{0:04}'.format(proc_id),
                                 'cat {0} {1} > {2}'.format(
                                   files[proc_id][0], files[proc_id][1],
                                   files[proc_id][2]));
      cond = taskrun.FileHashCondition(filedb,
                                       [files[proc_id][0], files[proc_id][1]],
                                       [files[proc_id][2]])
      task.add_condition(cond)
      evts.append('@{0}'.format(task.name))
      evts.append('*{0}'.format(task.name))
    ob.reinit(evts)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # change some
    rnd = random.Random()
    filedb = taskrun.FileHashDatabase(dbpath, 'md5')
    ob = OccurredCheckObserver([], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    evts = []
    for proc_id in range(procs):
      task = taskrun.ProcessTask(tm, 't{0:04}'.format(proc_id),
                                 'cat {0} {1} > {2}'.format(
                                   files[proc_id][0], files[proc_id][1],
                                   files[proc_id][2]));
      cond = taskrun.FileHashCondition(filedb,
                                       [files[proc_id][0], files[proc_id][1]],
                                       [files[proc_id][2]])
      task.add_condition(cond)
      # randomly sabotage this task
      evts.append('@{0}'.format(task.name))
      if bool(rnd.getrandbits(1)):
        evts.append('+{0}'.format(task.name))
        evts.append('-{0}'.format(task.name))
        # randomly select between sabotaging the input or output
        if bool(rnd.getrandbits(1)):
          # sabotage input (change input file)
          with open(files[proc_id][rnd.getrandbits(1)], 'w+') as ifile:
            print(str(rnd.getrandbits(8)), file=ifile)
        else:
          # sabotage output (delete output file)
          os.remove(files[proc_id][2])
      else:
        evts.append('*{0}'.format(task.name))
    ob.reinit(evts)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # no change
    filedb = taskrun.FileHashDatabase(dbpath, 'md5')
    ob = OccurredCheckObserver([], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    evts = []
    for proc_id in range(procs):
      task = taskrun.ProcessTask(tm, 't{0:04}'.format(proc_id),
                                 'cat {0} {1} > {2}'.format(
                                   files[proc_id][0], files[proc_id][1],
                                   files[proc_id][2]));
      cond = taskrun.FileHashCondition(filedb,
                                       [files[proc_id][0], files[proc_id][1]],
                                       [files[proc_id][2]])
      task.add_condition(cond)
      evts.append('@{0}'.format(task.name))
      evts.append('*{0}'.format(task.name))
    ob.reinit(evts)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # change some
    rnd = random.Random()
    filedb = taskrun.FileHashDatabase(dbpath, 'md5')
    ob = OccurredCheckObserver([], verbose=False)
    tm = taskrun.TaskManager(observer=ob)
    evts = []
    for proc_id in range(procs):
      task = taskrun.ProcessTask(tm, 't{0:04}'.format(proc_id),
                                 'cat {0} {1} > {2}'.format(
                                   files[proc_id][0], files[proc_id][1],
                                   files[proc_id][2]));
      cond = taskrun.FileHashCondition(filedb,
                                       [files[proc_id][0], files[proc_id][1]],
                                       [files[proc_id][2]])
      task.add_condition(cond)
      # randomly sabotage this task
      evts.append('@{0}'.format(task.name))
      if bool(rnd.getrandbits(1)):
        evts.append('+{0}'.format(task.name))
        evts.append('-{0}'.format(task.name))
        # randomly select between sabotaging the input or output
        if bool(rnd.getrandbits(1)):
          # sabotage input (change input file)
          with open(files[proc_id][rnd.getrandbits(1)], 'w+') as ifile:
            print(str(rnd.getrandbits(8)), file=ifile)
        else:
          # sabotage output (delete output file)
          os.remove(files[proc_id][2])
      else:
        evts.append('*{0}'.format(task.name))
    ob.reinit(evts)
    tm.run_tasks()
    self.assertTrue(ob.ok())
    filedb.write()

    # remove all files
    os.remove(dbpath)
    for proc_id in range(procs):
      for tfile in files[proc_id]:
        os.remove(tfile)
