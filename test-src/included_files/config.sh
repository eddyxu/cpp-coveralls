#!/bin/bash

#
# Only run in gcov mdoe: explicit inclusions are irrelevant when processing
# lcov files, these should already been done when manually assembling the lcov
# file...
#
modes="gcov"

gcov_coveralls_flags="-i foo.cpp"

