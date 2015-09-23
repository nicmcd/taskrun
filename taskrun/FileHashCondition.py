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
from .Condition import Condition
import os


class FileHashCondition(Condition):
  """
  This class uses lists of files to determine if a task should run. This
  condition takes a set of input files that are file based dependencies. This
  condition will have the task run if any of the files have changed since the
  last time. This condition takes a set of output files which the task would
  create or modify if it ran. This condition will have the task run if any of
  these files do not exist.
  """

  def __init__(self, filedb, inputs, outputs):
    """
    This constructs a FileHashCondition object

    Args:
      filedb (FileChangedDatabase) : a file database for checking file status
      inputs (list<str>)           : a list of filenames for the input files
      outputs (list<str>)          : a list of filenames for the output files
    """
    super(FileHashCondition, self).__init__()
    self._filedb = filedb
    self._inputs = inputs
    self._outputs = outputs

  def check(self):
    """
    See Condition.check()
    This implementation will return True if any of the output files do not exist
    or if the input files have changed
    """

    # don't make fast fail decisions, changed() needs to be called on all inputs
    ret = False
    for ofile in self._outputs:
      if not os.path.isfile(ofile):
        ret = True
    for ifile in self._inputs:
      if self._filedb.changed(ifile):
        ret = True
    return ret
