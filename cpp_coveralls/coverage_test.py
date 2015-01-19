#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2015 (c) Lei Xu <eddyxu@gmail.com>

import tempfile
import unittest

from . import coverage

class CoverageTest(unittest.TestCase):
    def test_exclude_pattern(self):
        """Test using regular expression for exclusion rules."""
        args = coverage.create_args(['-E', r'/abc.*\.txt'])
        self.assertTrue(coverage.is_excluded_path(args, '/abcd.txt'))
        self.assertFalse(coverage.is_excluded_path(args, '/cd.txt'))

    def test_mix_include_and_exclude_patten(self):
        """Test mix include pattens with exludes."""
        args = coverage.create_args(
            ("--include src --exclude src/not-this-file.c --exclude-pattern " +
            ".*useless.*").split())
        self.assertTrue(coverage.is_excluded_path(args,
                                                  "src/not-this-file.c"))
        self.assertFalse(coverage.is_excluded_path(args,
                                                   "src/but-this-file.c"))
        self.assertTrue(coverage.is_excluded_path(args,
                                                  "src/someuselessthing"))


    def test_try_encodings(self):
        with tempfile.NamedTemporaryFile(mode='wb') as output_file:
            output_file.write(b'\xe8')
            output_file.flush()

            assert coverage.try_encodings(output_file.name,
                                          ['utf-8', 'latin-1']) == 'latin-1'

            exception = None
            try:
                coverage.try_encodings(output_file.name,
                                       ['utf-8'])
            except ValueError as temporary:
                exception = temporary
            assert exception

if __name__ == '__main__':
    unittest.main()
