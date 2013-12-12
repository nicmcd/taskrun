from taskrun import *

manager = taskrun.Task.Manager(numProcs=2, showCommands=True, runTasks=True, showProgress=True)

task1 = manager.task_new("Task1", "cat LICENSE");
task2 = manager.task_new("Task2", "echo world hello!", "fun/output.txt");
task3 = manager.task_new("Task3", "mkdir fun");

task1.dependency_is(task2)
task2.dependency_is(task3)

manager.run_request_is()
