import random
import sys

try:
    import taskrun
except:
    print("'taskrun' doesn't appear to be installed. Did you install it?")
    print("You can install it locally by running:")
    print("python{2,3} setup.py install --user")
    sys.exit(-1)

manager = taskrun.Task.Manager(numProcs=20, showCommands=True, runTasks=True, \
                               showProgress=True)

vcs = [1, 2, 3, 4]
rates = [20, 40, 60, 80, 100]

random.seed(None)
def rsleep():
    return random.randint(1,3)

map_all = manager.new_task("Map_All", "sleep " + str(rsleep()))

reduce_all = manager.new_task("Reduce_All")

for vc in vcs:
    name = "Map_" + str(vc)
    cmd = "sleep " + str(rsleep())
    sub_map = manager.new_task(name, cmd)
    sub_map.add_dependency(map_all)

    name = "Reduce_" + str(vc)
    cmd = "sleep " + str(rsleep())
    sub_reduce = manager.new_task(name, cmd)
    reduce_all.add_dependency(sub_reduce)

    for rate in rates:
        name = "Worker_" + str(vc) + "-" + str(rate)
        cmd = "sleep 4"
        out = "/dev/null"
        task = manager.new_task(name, cmd, out)
        task.add_dependency(sub_map)
        sub_reduce.add_dependency(task)

reduce_all.set_command("sleep " + str(rsleep()))

manager.run_tasks()
