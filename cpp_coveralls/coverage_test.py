#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2015 (c) Lei Xu <eddyxu@gmail.com>

import tempfile
import unittest

from . import coverage

class CoverageTest(unittest.TestCase):
    def setUp(self):
        coverage._cached_exclude_rules = None

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


    def test_recursive_and_mixed_include_and_exclude_pattern(self):
        args = coverage.create_args(['-i', '/src/foo', '-i', '/src/bar',
                                     '-e', '/src/foo/subfoo', '-E', r'.*and.*'])
        self.assertTrue(coverage.is_excluded_path(args, '/foo.txt'))
        self.assertTrue(coverage.is_excluded_path(args, '/src/baz/baz.txt'))
        self.assertFalse(coverage.is_excluded_path(args, '/src/foo/foo.txt'))
        self.assertFalse(coverage.is_excluded_path(args, '/src/bar/foo.txt'))
        self.assertTrue(coverage.is_excluded_path(args, '/src/foo/foo-and-foo.txt'))
        self.assertTrue(coverage.is_excluded_path(args, '/src/bar/bar-and-bar.txt'))
        self.assertTrue(coverage.is_excluded_path(args, '/src/foo/subfoo/subfoo.txt'))

if __name__ == '__main__':
    unittest.main()
