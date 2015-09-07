# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .ComparisonCheckObserver import ComparisonCheckObserver
import numpy
import random
import unittest
import taskrun


rnd = random.Random()
rnd.seed()

def rsleep(m):
  return 'sleep {0}'.format(rnd.random() * m)

class MapReduceTestCase(unittest.TestCase):
  def text_mapreduce(self):
    vcs = numpy.arange(1, 8+1, 1)
    rates = numpy.arange(5, 100+1, 5)

    ob = ComparisonCheckObserver(0, [])
    tm = taskrun.TaskManager(observer=ob)

    # build all tasks
    map_all = taskrun.ProcessTask(tm, 'M', rsleep())
    reduce_all = taskrun.ProcessTask(tm, 'R', rsleep())

    for vc in vcs:
      map_vc = taskrun.ProcessTask(tm, 'M_{0}'.format(vc), rsleep())
      map_vc.add_dependency(map_all)

      reduce_vc = taskrun.ProcessTask(tm, 'R_{0}'.format(vc), rsleep())
      reduce_all.add_dependency(reduce_vc)

      for rate in rates:
        worker = taskrun.ProcessTask(tm, 'W_{0}_{1}'.format(vc, rate), rsleep())
        worker.add_dependency(map_vc)
        reduce_vc.add_dependency(worker)


    # build comparison list








  # CHANGE TEXT TO TEST
