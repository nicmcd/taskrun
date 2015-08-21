import random
import sys

try:
    import taskrun
except:
    print("'taskrun' doesn't appear to be installed. Did you install it?")
    print("You can install it locally by running:")
    print("python{2,3} setup.py install --user")
    sys.exit(-1)

manager = taskrun.Manager(numProcs=20, runTasks=True,
                          showDescriptions=True, showProgress=True)

vcs = [1, 2, 3, 4]
rates = [20, 40, 60, 80, 100]

random.seed(None)
def rsleep():
    return 0 #random.randint(1,3)

map_all = taskrun.ProcessTask(manager, "Map_All", "sleep " + str(rsleep()))

reduce_all = taskrun.ProcessTask(manager, "Reduce_All",
                                 "sleep " + str(rsleep()))

for vc in vcs:
    name = "Map_" + str(vc)
    cmd = "sleep " + str(rsleep())
    sub_map = taskrun.ProcessTask(manager, name, cmd)
    sub_map.add_dependency(map_all)

    name = "Reduce_" + str(vc)
    cmd = "sleep " + str(rsleep())
    sub_reduce = taskrun.ProcessTask(manager, name, cmd)
    reduce_all.add_dependency(sub_reduce)

    for rate in rates:
        name = "Worker_" + str(vc) + "-" + str(rate)
        cmd = "sleep " + str(rsleep())
        out = "/dev/null"
        task = taskrun.ProcessTask(manager, name, cmd, out)
        task.add_dependency(sub_map)
        sub_reduce.add_dependency(task)

manager.run_tasks()
