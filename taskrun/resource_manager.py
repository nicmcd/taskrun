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
from .resource import Resource


class ResourceManager:
  """
  This class manages a group of resources
  """

  def __init__(self, *args):
    """
    Constructs a ResourceManager object

    Args:
      *args = variable number of Resource objects
    """

    assert all(isinstance(arg, Resource) for arg in args), \
      'All arguments to ResourceManager must be taskrun.Resources'
    self._resources = args

  def can_start(self, task):
    """
    Determines if a task can start

    Args:
      task (Task) : the task under question
    """
    for resource in self._resources:
      if not resource.can_use(task):
        return False
    return True

  def start(self, task):
    """
    This method calls can_start() to see if the task can start. If successful,
    it then uses the resoures.

    Args:
      task (Task) : the task under question

    Returns:
      (bool) : True on success, False otherwise
    """
    if self.can_start(task):
      for resource in self._resources:
        res = resource.use(task)
        assert res
      return True
    return False

  def done(self, task):
    """
    Gives back the resources used by a task

    Args:
      task (Task) : the task under question
    """
    for resource in self._resources:
      resource.release(task)
