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
import unittest
import taskrun
import tempfile


class FileHashDatabaseTestCase(unittest.TestCase):
  def _db_tester(self, algo):
    fd, dbpath = tempfile.mkstemp()
    fd, file1 = tempfile.mkstemp()
    fd, file2 = tempfile.mkstemp()

    with open(file1, 'w') as fd:
      print('hello file1', file=fd)
    with open(file2, 'w') as fd:
      print('hello file2', file=fd)


    filedb = taskrun.FileHashDatabase(dbpath, algo)
    self.assertTrue(filedb.changed(file1))
    self.assertTrue(filedb.changed(file2))
    filedb.write()

    filedb = taskrun.FileHashDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    filedb.write()

    filedb = taskrun.FileHashDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    filedb.write()

    with open(file1, 'w') as fd:
      print('goodbye file1', file=fd)

    filedb = taskrun.FileHashDatabase(dbpath, algo)
    self.assertTrue(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    filedb.write()

    with open(file2, 'w') as fd:
      print('goodbye file2', file=fd)

    filedb = taskrun.FileHashDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertTrue(filedb.changed(file2))
    filedb.write()

    filedb = taskrun.FileHashDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    filedb.write()

    fd, file3 = tempfile.mkstemp()

    with open(file3, 'w') as fd:
      print('hello file3', file=fd)

    filedb = taskrun.FileHashDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    self.assertTrue(filedb.changed(file3))
    filedb.write()

    filedb = taskrun.FileHashDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    self.assertFalse(filedb.changed(file3))
    filedb.write()

    os.remove(dbpath)
    os.remove(file1)
    os.remove(file2)
    os.remove(file3)

  def test_md5(self):
    self._db_tester('md5')

  def test_sha1(self):
    self._db_tester('sha1')

  def test_sha224(self):
    self._db_tester('sha224')

  def test_sha256(self):
    self._db_tester('sha256')

  def test_sha384(self):
    self._db_tester('sha384')

  def test_sha512(self):
    self._db_tester('sha512')
