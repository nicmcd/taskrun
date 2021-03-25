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

from .condition import Condition


class FileModificationCondition(Condition):
  """
  This class uses lists of files to determine if a task should run. This
  condition takes a set of input files that are file based dependencies. This
  condition will have the task run if any of the input files are newer than the
  output files. This condition takes a set of output files which the task would
  create or modify if it ran. This condition will have the task run if any of
  the input or output files do not exist.
  """

  def __init__(self, inputs=None, outputs=None, verbose=False):
    """
    This constructs a FileModificationCondition object.

    Args:
      inputs (list<str>)           : a list of filenames for the input files
      outputs (list<str>)          : a list of filenames for the output files
      verbose (bool)               : print the results during check()
    """
    super().__init__()
    if inputs is None:
      inputs = []
    if outputs is None:
      outputs = []
    self.inputs = inputs
    self.outputs = outputs
    self.verbose = verbose

  def add_input(self, filename):
    """
    This adds a new file to the input file list

    Args:
      filename (str) : the filename to be added
    """
    self.inputs.append(filename)

  def add_output(self, filename):
    """
    This adds a new file to the output file list

    Args:
      filename (str) : the filename to be added
    """
    self.outputs.append(filename)

  def check(self):
    """
    See Condition.check()
    This implementation will return True if any of the output files do not
    exist or if the input files are newer than the outputs
    """

    # check for non-existent output files
    #  get minimum modification time of output files
    mtime = float('INF')
    mfile = None
    for ofile in self.outputs:
      if not os.path.isfile(ofile):
        if self.verbose:
          print('{} does not exist'.format(ofile))
        return True
      new_mtime = os.path.getmtime(ofile)
      if new_mtime < mtime:
        mtime = new_mtime
        mfile = ofile

    # check whether any input file is newer than the minimum output file
    #  modification time
    for ifile in self.inputs:
      if not os.path.isfile(ifile):
        if self.verbose:
          print('{} does not exist'.format(ifile))
        return True
      if os.path.getmtime(ifile) >= mtime:
        if self.verbose:
          print('{} is newer than {}'.format(ifile, mfile))
        return True

    # all tests passed, don't need to run task
    return False
