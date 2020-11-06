#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#

import io
import unittest

from . import coverage


class ParseGcovTest(unittest.TestCase):
    # test template example from the documentation (https://gcc.gnu.org/onlinedocs/gcc/Invoking-Gcov.html#Invoking-Gcov)
    def test_templated_coverage(self):
        args = coverage.create_args("")
        f = io.BytesIO(b"""
        -:    0:Source:tmp.cpp
        -:    0:Working directory:/home/gcc/testcase
        -:    0:Graph:tmp.gcno
        -:    0:Data:tmp.gcda
        -:    0:Runs:1
        -:    0:Programs:1
        -:    1:#include <stdio.h>
        -:    2:
        -:    3:template<class T>
        -:    4:class Foo
        -:    5:{
        -:    6:  public:
       1*:    7:  Foo(): b (1000) {}
------------------
Foo<char>::Foo():
    #####:    7:  Foo(): b (1000) {}
------------------
Foo<int>::Foo():
        1:    7:  Foo(): b (1000) {}
------------------
        """)
        parsed_lines = coverage.parse_gcov_file(args, f, "bar")
        self.assertEqual(7, len(parsed_lines))
        self.assertEqual(1, parsed_lines[6])
