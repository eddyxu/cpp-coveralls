#!/usr/bin/env python
#
# Copyright 2014 (c) Lei Xu <eddyxu@gmail.com>

import tempfile

from . import coverage


def test_exclude_pattern():
    """Test using regular expression for exclusion rules."""
    args = coverage.create_args(['-E', r'/abc.*\.txt'])
    assert coverage.is_excluded_path(args, '/abcd.txt')
    assert not coverage.is_excluded_path(args, '/cd.txt')


def test_try_encodings():
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
