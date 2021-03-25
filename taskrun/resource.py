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

class Resource:
  """
  This class defines the abstract interface for a resource
  """

  def __init__(self, name, default):
    """
    Constructs a Resource object

    Args:
      name (str) : the name of the resource
      default    : the default value for this resource
    """
    self._name = name
    self._default = default

  @property
  def name(self):
    """
    Returns:
      (str) : name of this Resource
    """
    return self._name

  @name.setter
  def name(self, value):
    """
    Sets the name of this Resource

    Args:
      value (str) : the new name
    """
    self._name = value

  @property
  def default(self):
    """
    Returns:
      the default value
    """
    return self._default

  @default.setter
  def default(self, value):
    """
    Sets the default value of this Resource

    Args:
      value (num) : the new default value
    """
    self._default = value

  def can_use(self, task):
    """
    This method checks if the specified task could use the resource

    Args:
      task (Task) : the task desiring to use the resource
    """
    raise NotImplementedError('subclasses must override this')

  def use(self, task):
    """
    This method checks and uses a resource by the specified task

    Args:
      task (Task) : the task desiring to use the resource

    Returns:
      (bool) : returns True if successful, False otherwise
    """
    raise NotImplementedError('subclasses must override this')

  def release(self, task):
    """
    This method releases the resource used by the specified task

    Args:
      task (Task) : the task releasing the resource
    """
    raise NotImplementedError('subclasses must override this')
