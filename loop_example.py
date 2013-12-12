#!/usr/bin/env python

import random
import sys

try:
    import taskrun
except:
    print("'taskrun' doesn't appear to be installed. Did you install it?")
    print("You can install it locally by running:")
    print("python setup.py install --user")
    sys.exit(-1)

manager = taskrun.Task.Manager(numProcs=20, showCommands=True, runTasks=True, showProgress=True)

vcs = [1, 2, 3, 4]
rates = [20, 40, 60, 80, 100]

random.seed(None)
def rsleep():
    return random.randint(1,3)

name = "Map_All"
cmd = "sleep " + str(rsleep())
map_all = manager.task_new(name, cmd)

name = "Reduce_All"
cmd = "sleep " + str(rsleep())
reduce_all = manager.task_new(name, cmd)

for vc in vcs:
    name = "Map_" + str(vc)
    cmd = "sleep " + str(rsleep())
    sub_map = manager.task_new(name, cmd)
    sub_map.dependency_is(map_all)

    name = "Reduce_" + str(vc)
    cmd = "sleep " + str(rsleep())
    sub_reduce = manager.task_new(name, cmd)
    reduce_all.dependency_is(sub_reduce)

    for rate in rates:
        name = "Worker_" + str(vc) + "-" + str(rate)
        cmd = "sleep 4"
        out = "/dev/null"
        task = manager.task_new(name, cmd, out)
        task.dependency_is(sub_map)
        sub_reduce.dependency_is(task)

manager.run_request_is()
