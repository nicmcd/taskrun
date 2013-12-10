import random
from taskrun import *

manager = taskrun.Manager()

vcs = [1, 2, 3, 4]
rates = [20, 40, 60, 80, 100]

random.seed(None)

name = "Map_All"
map_all = taskrun.Task(name)
map_all.addCommand("echo " + name)
manager.addTask(map_all)

name = "Reduce_All"
reduce_all = taskrun.Task(name)
reduce_all.addCommand("echo " + name)
manager.addTask(reduce_all)

for vc in vcs:
    name = "Map_" + str(vc)
    sub_map = taskrun.Task(name)
    sub_map.addCommand("echo " + name)
    sub_map.addDependency(map_all)
    manager.addTask(sub_map)

    name = "Reduce_" + str(vc)
    sub_reduce = taskrun.Task(name)
    sub_reduce.addCommand("echo " + name)
    reduce_all.addDependency(sub_reduce)
    manager.addTask(sub_reduce)

    for rate in rates:
        name = "Worker_" + str(vc) + "-" + str(rate)
        pause = "; sleep " + str(random.randint(1,3))
        task = taskrun.Task(name)
        task.addCommand("echo " + name + pause)
        task.addDependency(sub_map)
        sub_reduce.addDependency(task)
        manager.addTask(task)

manager.runTasks()
