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

# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import math
import os
import resource
import psutil
from .ProcessTask import ProcessTask
from .Resource import Resource
from .SlurmTask import SlurmTask


class SlurmResource(Resource):
  """
  This class implements a Slurm resource. This implementation is used when an
  allocation has been giving by Slurm and the Taskrun program is being run
  within the allocation. This module will assign tasks to particular nodes
  within the Slurm allocation.
  """

  def __init__(self, name, default):
    """
    Constructs a SlurmResource object

    Args:
      name (str)    : the name of the resource
      default (num) : default value of tasks that don't specify it (in threads)
    """
    super(SlurmResource, self).__init__(name, default)

    # This retrieves the list of nodes from the SLURM_NODELIST environment
    #  variable and uses the SLURM_NTASKS_PER_NODE to assign each node a count
    #  value of how many threads are available to each node

    # pull info from the environment variable
    assert 'SLURM_NODELIST' in os.environ
    nodelist = os.environ['SLURM_NODELIST'].strip(',')

    # find comma locations outside of brackets
    divs = []
    block = False
    for idx in range(len(nodelist)):
      c = nodelist[idx]
      if c == '[':
        assert not block
        block = True
      elif c == ',':
        if not block:
          divs.append(idx)
      elif c == ']':
        assert block
        block = False

    # make blocks
    blocks = []
    bottom = 0
    for div in divs:
      assert bottom < div
      block = nodelist[bottom:div]
      blocks.append(block)
      bottom += len(block) + 1
      bottom
    blocks.append(nodelist[bottom:])

    # node list
    nodes = []

    # iterate over blocks
    for block in blocks:
      assert block.find('[') != 0

      # bail out early
      if block.find('[') < 0:
        assert block not in nodes, 'duplicate node found'
        nodes.append(block)
        continue

      # expand ranges
      assert block.find(']') == len(block)-1
      base = block[0:block.find('[')]
      num_desc = block[block.find('[')+1:-1]
      nums = []
      for span in num_desc.split(','):
        if span.find('-') < 0:
          assert int(span) not in nums, 'duplicate node found'
          nums.append(int(span))
        else:
          start = int(span[0:span.find('-')])
          stop = int(span[span.find('-')+1:])
          for num in range(start, stop+1):
            assert int(num) not in nums, 'duplicate node found'
            nums.append(int(num))

      # add all
      for num in nums:
        node = base + str(num)
        assert node not in nodes, 'duplicate node found'
        nodes.append(node)

    # verify correct number of nodes
    assert 'SLURM_NNODES' in os.environ
    assert int(os.environ['SLURM_NNODES']) == len(nodes)

    # get number of threads per node
    assert 'SLURM_NTASKS_PER_NODE' in os.environ
    self._threads_per_node = int(os.environ['SLURM_NTASKS_PER_NODE'])

    # verify total number is correct
    assert 'SLURM_NTASKS' in os.environ
    assert (int(os.environ['SLURM_NTASKS']) ==
            (len(nodes) * self._threads_per_node))

    # create map of remaining number of threads for each node
    self._nodes = {}
    for node in nodes:
      self._nodes[node] = self._threads_per_node

  def can_use(self, task):
    """
    See Resource.can_use()
    """

    # return early if this is not a SlurmTask
    if not isinstance(task, SlurmTask):
      return True

    # determine number of threads this task needs
    uses = task.resource(self.name)
    if uses is None:
      uses = self.default

    # ensure it isn't asking for too much
    if uses > self._threads_per_node:
      raise ValueError('task \'{0}\' uses {1} threads of resource \'{2}\''
                       ' but there is only {3} threads per node'
                       .format(task.name, uses, self.name,
                               self._threads_per_node))

    # attempt to find a node to fit in
    for node in self._nodes:
      if uses <= self._nodes[node]:
        return True
    return False

  def use(self, task):
    """
    See Resource.use()
    """

    # return early if this is not a SlurmTask
    if not isinstance(task, SlurmTask):
      return True

    # determine number of threads this task needs
    uses = task.resource(self.name)
    if uses is None:
      uses = self.default

    # ensure it isn't asking for too much
    if uses > self._threads_per_node:
      raise ValueError('task \'{0}\' uses {1} threads of resource \'{2}\''
                       ' but there is only {3} threads per node'
                       .format(task.name, uses, self.name,
                               self._threads_per_node))

    # attempt to find a node to fit in
    for node in self._nodes:
      if uses <= self._nodes[node]:
        # reduce the count of threads
        self._nodes[node] -= uses
        task.node = node
        return True
    return False

  def release(self, task):
    """
    See Resource.release()
    """

    # return early if this is not a SlurmTask
    if not isinstance(task, SlurmTask):
      return True

    # determine number of threads this task needs
    uses = task.resource(self.name)
    if uses is None:
      uses = self.default
    assert uses <= self._threads_per_node

    # give back threads to node
    assert task.node in self._nodes
    self._nodes[task.node] += uses
