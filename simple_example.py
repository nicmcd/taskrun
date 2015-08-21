import sys

try:
    import taskrun
except ImportError:
    print("'taskrun' doesn't appear to be installed. Did you install it?")
    print("You can install it locally by running:")
    print("python{2,3} setup.py install --user")
    sys.exit(-1)

def doit(first, *args, **kwargs):
  print('first:')
  print('  {0}'.format(first))
  print('args:')
  for a in args:
    print('  {0}'.format(a))
  print('kwargs:')
  for k in kwargs:
    print('  {0}->{1}'.format(k, kwargs[k]))

# create a task manager
manager = taskrun.Manager(numProcs=2, runTasks=True,
                          showDescriptions=True, showProgress=True)

# create some tasks
task1 = taskrun.ProcessTask(manager, "Task1", "cat LICENSE");
task2 = taskrun.ProcessTask(manager, "Task2", "echo world hello!",
                            "/tmp/fun/output.txt");
task3 = taskrun.ProcessTask(manager, "Task3", "mkdir -p /tmp/fun");
task4 = taskrun.FunctionTask(manager, "Task4", doit, 1, 2, 3, age=29, car='BMW')

# set task dependencies
task1.add_dependency(task2)
task2.add_dependency(task3)
task4.add_dependency(task1)
task4.add_dependency(task2)
task4.add_dependency(task3)

# run all tasks
manager.run_tasks()
