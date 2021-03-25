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
import functools
import hashlib
import os
import threading


class FileHashDatabase:
  """
  This class maintains a database of file change history. It only tracks if
  files have changed since last time it ran.
  """

  def __init__(self, filename, algorithm='sha1'):
    """
    This constructs a FileHashDatabase object.

    Notes:
      The input 'algorithm' can be md5, sha1, sha224, sha256, sha384, or sha512

    Args:
      filename (str)  : filename of database
      algorithm (str) : algorithm name of hash
    """

    # attempt to make a hash using the specified algorithm
    self._hash_const = None
    if algorithm == 'md5':
      self._hash_const = hashlib.md5
    elif algorithm == 'sha1':
      self._hash_const = hashlib.sha1
    elif algorithm == 'sha224':
      self._hash_const = hashlib.sha224
    elif algorithm == 'sha256':
      self._hash_const = hashlib.sha256
    elif algorithm == 'sha384':
      self._hash_const = hashlib.sha384
    elif algorithm == 'sha512':
      self._hash_const = hashlib.sha512
    else:
      raise ValueError('invalid hash algorithm: {0}'.format(algorithm))

    self._filename = filename
    self._hashes = {}  # hashes read in from the database (previous run)

    if os.path.isfile(self._filename):
      assert os.access(self._filename, os.R_OK)
      assert os.access(self._filename, os.W_OK)
      with open(self._filename, 'r') as ifile:
        for line in ifile.readlines():
          words = line.strip().split()
          assert len(words) == 2
          self._hashes[words[0]] = words[1]
    self._files = set(self._hashes.keys())  # files to be hashed this round

    self._changed = set()
    self._lock = threading.Lock()

  def write(self):
    """
    This writes the file database out to the file
    """
    with self._lock:
      with open(self._filename, 'w') as ofile:
        for filename in self._files:
          hasher = self._hash_const()
          with open(filename, mode='rb') as ifile:
            for buf in iter(functools.partial(ifile.read, 1024), b''):
              hasher.update(buf)
          digest = hasher.hexdigest()
          print('{0} {1}'.format(filename, digest), file=ofile)

  def changed(self, filename):
    """
    This checks if a file has changed or not

    Args:
      filename (str) : the file to check for change
    """

    with self._lock:
      # check the changed list first
      if filename in self._changed:
        return True

      ret = False

      # if not in the database, say it changed
      if filename not in self._hashes:
        # add the filename to the list of files to watch
        self._files.add(filename)
        ret = True

      # handle already in the database
      else:
        # generate the current hash
        hasher = self._hash_const()
        with open(filename, 'r') as ifile:
          hasher.update(ifile.read().encode('utf-8'))
        digest = hasher.hexdigest()

        # check against previous hash
        ret = digest != self._hashes[filename]

      # keep a memo of changed files
      if ret:
        self._changed.add(filename)

      return ret
