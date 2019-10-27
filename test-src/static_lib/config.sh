#!/bin/bash
gcc_version=$($CXX -v 2>&1 | awk '/gcc version/ {print $3}')
if [[ "$gcc_version" < "8" ]]; then
    gcov_fail_reason=""
else
    gcov_fail_reason="cpp-coveralls parser does not support modern gcov's output"
fi
