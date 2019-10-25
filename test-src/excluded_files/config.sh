#!/bin/bash

#
# Only run in gcov mdoe: exclusions are irrelevant when processing lcov files,
# these should already been done when manually assembling the lcov file...
#
modes="gcov"

gcov_coveralls_flags="-e part_unused.cpp -e part_unused.h -e extra_lib -E .*another_extra_lib.*"

