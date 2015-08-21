import sys

try:
    import taskrun
except:
    print("'taskrun' doesn't appear to be installed. Did you install it?")
    print("You can install it locally by running:")
    print("python{2,3} setup.py install --user")
    sys.exit(-1)

# create a task manager
manager = taskrun.Manager(numProcs=2, showCommands=True, runTasks=True,
                          showProgress=True)

# create some tasks
task1 = manager.new_task("Task1", "cat LICENSE");
task2 = manager.new_task("Task2", "echo world hello!", "fun/output.txt");
task3 = manager.new_task("Task3", "mkdir fun");

# set task dependencies
task1.add_dependency(task2)
task2.add_dependency(task3)

# run all tasks
manager.run_tasks()
