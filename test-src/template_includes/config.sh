#!/bin/bash

# Set if we expect the GCOV test for a known reason
gcc_version=$($CXX -v 2>&1 | awk '/gcc version/ {print $3}')
if [[ "$gcc_version" < "8" ]]; then
    gcov_fail_reason=""
else
    gcov_fail_reason="cpp-coveralls parser does not support modern gcov's output"
fi

# Set if we expect the LCOV test for a known reason
lcov_fail_reason=""

# Set to provide additional flags to cpp-coveralls when in lcov mode
lcov_coveralls_flags=""
