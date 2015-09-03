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
#ob = taskrun.Observer(show_starting=False, show_completed=False)
tm = taskrun.TaskManager(rm, ob)

vcs = numpy.arange(1, 33, 1)
rates = numpy.arange(1, 101, 1)

random.seed(None)
def rsleep():
  return 0 #random.randint(1,3)

map_all = taskrun.ProcessTask(tm, "Map_All",
                              "sleep " + str(rsleep()))

reduce_all = taskrun.ProcessTask(tm, "Reduce_All",
                                 "sleep " + str(rsleep()))

for vc in vcs:
  name = "Map_" + str(vc)
  cmd = "sleep " + str(rsleep())
  sub_map = taskrun.ProcessTask(tm, name, cmd)
  sub_map.add_dependency(map_all)

  name = "Reduce_" + str(vc)
  cmd = "sleep " + str(rsleep())
  sub_reduce = taskrun.ProcessTask(tm, name, cmd)
  reduce_all.add_dependency(sub_reduce)

  for rate in rates:
    name = "Worker_" + str(vc) + "-" + str(rate)
    cmd = "sleep " + str(rsleep())
    task = taskrun.ProcessTask(tm, name, cmd)
    task.add_dependency(sub_map)
    sub_reduce.add_dependency(task)

num = tm.num_tasks()
start = time.time()
tm.run_tasks()
stop = time.time()
elapsed = stop - start
print('tasks={0} / secs={1} --> task_per_sec={2}'
      .format(num, elapsed, num / elapsed))
