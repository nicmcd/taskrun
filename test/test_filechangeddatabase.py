# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import unittest
import taskrun
import tempfile


class FileChangedDatabaseTestCase(unittest.TestCase):
  def _db_tester(self, algo):
    fd, dbpath = tempfile.mkstemp()
    fd, file1 = tempfile.mkstemp()
    fd, file2 = tempfile.mkstemp()

    with open(file1, 'w') as fd:
      print('hello file1', file=fd)
    with open(file2, 'w') as fd:
      print('hello file2', file=fd)


    filedb = taskrun.FileChangedDatabase(dbpath, algo)
    self.assertTrue(filedb.changed(file1))
    self.assertTrue(filedb.changed(file2))
    filedb.write()

    filedb = taskrun.FileChangedDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    filedb.write()

    filedb = taskrun.FileChangedDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    filedb.write()

    with open(file1, 'w') as fd:
      print('goodbye file1', file=fd)

    filedb = taskrun.FileChangedDatabase(dbpath, algo)
    self.assertTrue(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    filedb.write()

    with open(file2, 'w') as fd:
      print('goodbye file2', file=fd)

    filedb = taskrun.FileChangedDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertTrue(filedb.changed(file2))
    filedb.write()

    filedb = taskrun.FileChangedDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    filedb.write()

    fd, file3 = tempfile.mkstemp()

    with open(file3, 'w') as fd:
      print('hello file3', file=fd)

    filedb = taskrun.FileChangedDatabase(dbpath, algo)
    self.assertFalse(filedb.changed(file1))
    self.assertFalse(filedb.changed(file2))
    self.assertTrue(filedb.changed(file3))
    filedb.write()

    filedb = taskrun.FileChangedDatabase(dbpath, algo)
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
