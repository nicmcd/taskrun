"""
Copyright (c) 2013-2015, Nic McDonald
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import multiprocessing
import os
import subprocess
import threading
import time
import sys


"""
This class manages a group of resources
"""
class ResourceManager(object):

  def __init__(self, *args):
    self._resources = args;
    self._access_lock = threading.Lock()

  def can_run(self, task):
    res = True

    # lock access
    self._access_lock.acquire()

    # verify for all resources
    for resource in self._resources:
      # get consumption by task
      consumes = task.resource(resource.name)
      if consumes is None:
        consumes = resource.default

      # check if there is enough resource left
      if consumes > resource.total:
        raise RuntimeError('task \'{0}\' consumes {1} units of resource \'{2}\''
                           ' but there is only {3} units total'
                           .format(task.name, consumes, resource.name,
                                   resource.total))
      elif resource.amount < consumes:
        res = False
        break;

    # release access and return
    self._access_lock.release()
    return res

  def task_starting(self, task):
    res = True

    # lock access
    self._access_lock.acquire()

    # check all resources
    for resource in self._resources:
      # get consumption by task
      consumes = task.resource(resource.name)
      if consumes is None:
        consumes = resource.default

      # check if there is enough resource left
      if consumes > resource.total:
        raise RuntimeError('task \'{0}\' consumes {1} units of resource \'{2}\''
                           ' but there is only {3} units total'
                           .format(task.name, consumes, resource.name,
                                   resource.total))
      elif resource.amount < consumes:
        res = False
        break;

    # if can start, decrement resources
    if res == True:
      for resource in self._resources:
        # get consumption by task
        consumes = task.resource(resource.name)
        if consumes is None:
          consumes = resource.default

        # decrement resource
        resource.amount -= consumes

    # release access and return
    self._access_lock.release()
    return res

  def task_completed(self, task):
    # lock access
    self._access_lock.acquire()

    # increment all resources
    for resource in self._resources:
      # get consumption by task
      consumes = task.resource(resource.name)
      if consumes is None:
        consumes = resource.default

      # increment resource
      resource.amount += consumes

    # release access and return
    self._access_lock.release()