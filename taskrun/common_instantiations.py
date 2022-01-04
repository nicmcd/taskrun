"""
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""

import os

from .counter_resource import CounterResource
from .failure_mode import FailureMode
from .file_cleanup_observer import FileCleanupObserver
from .memory_resource import MemoryResource
from .resource_manager import ResourceManager
from .task_manager import TaskManager
from .verbose_observer import VerboseObserver


def standard_task_manager(
    track_cpus=True,
    max_cpus=-1,
    default_cpus=999999999,
    track_memory=True,
    max_memory=-1,
    default_memory=999999999,
    verbosity=1,
    log_file=None,
    cleanup_files=True,
    failure_mode='aggressive_fail'):
  """Creates a standard task manager.

  Args:
    track_cpus     (bool) - track CPU resources as 'cpus'
    max_cpus       (num)  - maximum CPUs, <=0 for num_procs
    default_cpus   (num)  - default CPUs per tasks
    track_memory   (bool) - track memory resources as 'mem'
    max_memory     (num)  - maximum memory in GiB, <=0 for currently available
    default_memory (num)  - default memory per tasks in GiB
    verbosity      (int)  - 0=off, 1=minimal, 2=full
    log_file       (str)  - a file to write log to, None for none
    cleanup_files  (bool) - remove output files of tasks on failure
    failure_mode   (FM)   - failure mode, see failure_mode.py create()

  Returns:
    task_manager (TaskManager)
  """
  resources = []
  if track_cpus:
    if max_cpus <= 0:
      cpus = os.cpu_count()
    else:
      cpus = max_cpus
    resources.append(CounterResource('cpus', default_cpus, cpus))
  if track_memory:
    if max_memory <= 0:
      mem = MemoryResource.current_available_memory_gib()
    else:
      mem = max_memory
    resources.append(MemoryResource('mem', default_memory, mem))
  resource_manager = ResourceManager(*resources)

  return __create_standard_task_manager(
    resource_manager, verbosity, log_file, cleanup_files, failure_mode)


def basic_task_manager(
    parallelism=1,
    verbosity=1,
    cleanup_files=True,
    failure_mode='aggressive_fail'):
  """Creates a task manager that executes tasks with N-way parallelism.

  The resource created is called 'slots'. By default each task takes 1 slot.

  Args:
    parallelism    (int)  - amount of parallelism (<=0 for num_procs)
    verbosity      (int)  - 0=off, 1=minimal, 2=full
    cleanup_files  (bool) - remove output files of tasks on failure
    failure_mode   (FM)   - failure mode, see failure_mode.py create()

  Returns:
    task_manager (TaskManager)
  """
  resources = []
  if parallelism <= 0:
    slots = os.cpu_count()
  else:
    slots = parallelism
  resources.append(CounterResource('slots', 1, slots))
  resource_manager = ResourceManager(*resources)
  return __create_standard_task_manager(
    resource_manager, verbosity, None, cleanup_files, failure_mode)


def __create_task_manager(rm, obs, fm):
  return TaskManager(resource_manager=rm, observers=obs, failure_mode=fm)


def __create_standard_task_manager(rm, verbosity, log_file, cleanup_files,
                                   failure_mode):
  observers = []
  if verbosity > 0:
    full_verbosity = verbosity > 1
    log = None
    if log_file:
      log = open(log_file, 'w')
    observers.append(VerboseObserver(
      log=log,
      show_kills=full_verbosity,
      show_descriptions=full_verbosity,
      show_current_time=full_verbosity))
  if cleanup_files:
    observers.append(FileCleanupObserver())
  failure_mode = FailureMode.create(failure_mode)
  return __create_task_manager(rm, observers, failure_mode)
