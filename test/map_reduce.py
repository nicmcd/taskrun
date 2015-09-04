#!/usr/bin/env python3

import multiprocessing
import numpy
import random
import sys
import time

import taskrun

# create a resource manager
rm = taskrun.ResourceManager(
  taskrun.Resource('cpu', 1, multiprocessing.cpu_count()),
  taskrun.Resource('mem', 500, 8000))

# create a task manager
ob = taskrun.Observer(show_starting=True, show_completed=True)
tm = taskrun.TaskManager(rm, ob)

vcs = numpy.arange(1, 5, 1)
rates = numpy.arange(20, 101, 20)

rnd = random.Random()
rnd.seed()
def randSleep(m=5):
  return "sleep " + str(rnd.randint(1, m))

map_all = taskrun.ProcessTask(tm, "Map_All", randSleep())
reduce_all = taskrun.ProcessTask(tm, "Reduce_All", randSleep())

for vc in vcs:
  name = "Map_" + str(vc)
  sub_map = taskrun.ProcessTask(tm, name, randSleep())
  sub_map.add_dependency(map_all)

  name = "Reduce_" + str(vc)
  sub_reduce = taskrun.ProcessTask(tm, name, randSleep())
  reduce_all.add_dependency(sub_reduce)

  for rate in rates:
    name = "Worker_" + str(vc) + "-" + str(rate)
    worker = taskrun.ProcessTask(tm, name, randSleep())
    worker.add_dependency(sub_map)
    sub_reduce.add_dependency(worker)

num = tm.num_tasks()
print('{0} tasks to run'.format(num))

tm.run_tasks()
