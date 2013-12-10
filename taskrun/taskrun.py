import multiprocessing
import os
import subprocess
import threading
import time


###############################################################################
# This defines one task
###############################################################################
class Task(threading.Thread):

    class Status:
        WAITING = "waiting"
        READY = "ready"
        RUNNING = "running"
        DONE = "done"

    def __init__(self, name):
        threading.Thread.__init__(self)
        self._name = name
        self._countLock = None
        self._commands = []
        self._dependencies = []
        self._status = self.Status.READY
        self._statusLock = threading.Lock()
        self._show = False
        self._run = True

    def name(self):
        return self._name;

    def addCommand(self, command, output=None):
        self._commands.append((command, output))

    def addDependency(self, runner):
        self._dependencies.append(runner)

    def setLock(self, countLock):
        self._countLock = countLock

    def setShow(self, show):
        self._show = show

    def setRun(self, run):
        self._run = run

    def __setStatus(self, status):
        self._statusLock.acquire(True)
        self._status = status
        self._statusLock.release()

    def getStatus(self):
        self._statusLock.acquire(True)
        status = self._status
        self._statusLock.release()
        if status == self.Status.DONE or status == self.Status.RUNNING:
            return status
        else:
            for task in self._dependencies:
                if task.getStatus() != self.Status.DONE:
                    return self.Status.WAITING
            return self.Status.READY

    def run(self):
        self.__setStatus(self.Status.RUNNING)
        for command_set in self._commands:
            command = command_set[0]
            output  = command_set[1]
            if self._show:
                if output:
                    print("[" + self._name + "]: " + command + " &> " + str(output))
                else:
                    print("[" + self._name + "]: " + command)
            if self._run:
                if output is not None:
                    ofd = open(output, 'w')
                    proc = subprocess.Popen(command, stdout=ofd, stderr=ofd, shell=True)
                else:
                    proc = subprocess.Popen(command, shell=True)
                proc.wait()
                if output is not None:
                    ofd.close()
                if proc.returncode != 0:
                    print("[" + self._name + "] ERROR: " + command)
                    os._exit(-1)
        self._countLock.decrement()
        self.__setStatus(self.Status.DONE)


###############################################################################
# This manages many Tasks
###############################################################################
class Manager():

    def __init__(self, num_procs=multiprocessing.cpu_count()):
        self._num_procs = num_procs
        self._countLock = CountLock()
        self._tasks = []

    def addTask(self, task):
        task.setLock(self._countLock)
        self._tasks.append(task)

    def runTasks(self, show=False, run=True, progress=True):

        total_tasks = len(self._tasks)

        if show:
            for task in self._tasks:
                task.setShow(True)

        if not run:
            for task in self._tasks:
                task.setRun(False)

        remaining_tasks = len(self._tasks)
        while remaining_tasks > 0:

            # print the progress
            if progress:
                proc_num = total_tasks - remaining_tasks
                percent = (proc_num / total_tasks) * 100.00
                print("%(percent).0f%% (%(proc_num)d of %(total_tasks)d)" % {\
                        'percent' : round(percent, 0), \
                            'proc_num' : proc_num, \
                            'total_tasks' : total_tasks })

            # wait for an available process slot
            while self._countLock.count() >= self._num_procs:
                time.sleep(1)

            # search the tasks for a ready task
            found_task = False
            while not found_task:

                # search the task list to find a ready task
                for task in self._tasks:
                    if task.getStatus() == Task.Status.READY:
                        self._countLock.increment()
                        task.start()
                        found_task = True
                        break

                # if no tasks were ready, sleep then search again
                if not found_task:
                    time.sleep(1)

            # decrement the remaining tasks count
            remaining_tasks -= 1

        if progress:
            proc_num = total_tasks - remaining_tasks
            percent = (proc_num / total_tasks) * 100.00
            print("%(percent).0f%% (%(proc_num)d of %(total_tasks)d)" % {\
                    'percent' : round(percent, 0), \
                        'proc_num' : proc_num, \
                        'total_tasks' : total_tasks })


###############################################################################
# This is a simple counter object that is thread safe
###############################################################################
class CountLock:

    def __init__(self):
        self._lock  = threading.Lock()
        self._count = 0;

    def count(self):
        self._lock.acquire(True)
        cnt = self._count
        self._lock.release()
        return cnt

    def increment(self):
        self._lock.acquire(True)
        self._count += 1
        self._lock.release()

    def decrement(self):
        self._lock.acquire(True)
        self._count -= 1
        self._lock.release()
