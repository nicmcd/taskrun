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


class Resource(object):
  """
  This class represents one resource being consumed
  """

  def __init__(self, name, default, total):
    """
    Constructs a Resource object

    Args:
      name (str)    : the name of the resource
      default (num) : default value of tasks that don't specify it
      total (num)   : total available to be used by tasks
    """

    self._name = name
    self._default = default
    self._total = total
    self._amount = total

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
      (num) : the default value
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

  @property
  def total(self):
    """
    Returns:
      (num) : the total amount of this resource
    """
    return self._total

  @total.setter
  def total(self, value):
    """
    Sets the total amount of this Resource

    Args:
      value (num) : the new total amount
    """
    self._total = value

  @property
  def amount(self):
    """
    Returns:
      (num) : the current amount of this Resource
    """
    return self._amount

  @amount.setter
  def amount(self, value):
    """
    Sets the current amount of this resource

    Args:
      value (num) : the new current amount
    """

    self._amount = value
    assert self._amount >= 0
    assert self._amount <= self._total
