"""
 * Copyright (c) 2012-2016, Nic McDonald
 * All rights reserved.
 *
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
 * - Neither the name of prim nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
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
from enum import Enum, unique


@unique
class FailureMode(Enum):
  """
  This enum class defines a set of failure modes for a TaskManager object
  """

  # This mode immediately kills all currently running tasks
  AGGRESSIVE_FAIL = 1

  # This mode allows the current running jobs to complete before ending
  PASSIVE_FAIL = 2

  # This mode continues execution of all jobs not associated with the failure
  ACTIVE_CONTINUE = 3

  # This mode pretends failures don't exist and continues executing as if the
  #  failure didn't happen
  BLIND_CONTINUE = 4

  @staticmethod
  def create(val):
    """
    This function returns a FailureMode object by parsing the input. The input
    can be a FailureMode, the integer value, or the string value

    Args:
      val (FailureMode, int, str) : the failure mode to return in Enum form

    Returns:
      FailureMode object
    """

    if isinstance(val, FailureMode):
      return val

    elif isinstance(val, int):
      return FailureMode(val)

    elif isinstance(val, str):
      if val.lower() == 'aggressive_fail':
        return FailureMode.AGGRESSIVE_FAIL
      elif val.lower() == 'passive_fail':
        return FailureMode.PASSIVE_FAIL
      elif val.lower() == 'active_continue':
        return FailureMode.ACTIVE_CONTINUE
      elif val.lower() == 'blind_continue':
        return FailureMode.BLIND_CONTINUE
      else:
        raise ValueError('invalid FailureMode str {0}'.format(val))

    else:
      raise TypeError('invalid input type to FailureMode.create(): {0}'
                      .format(type(val)))
