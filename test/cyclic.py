#!/usr/bin/env python3

import taskrun

rm = taskrun.ResourceManager()
tm = taskrun.TaskManager(rm, None)

t1 = taskrun.ProcessTask(tm, 'T1', '')
t2 = taskrun.ProcessTask(tm, 'T2', '')
t3 = taskrun.ProcessTask(tm, 'T3', '')
t4 = taskrun.ProcessTask(tm, 'T4', '')
t5 = taskrun.ProcessTask(tm, 'T5', '')
t1.add_dependency(t2)
t2.add_dependency(t3)
t3.add_dependency(t4)
t4.add_dependency(t5)
#t5.add_dependency(t1)  # uncommenting this breaks
