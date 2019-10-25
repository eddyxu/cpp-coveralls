#!/bin/bash

# Override to change the file that contains the expected output for the gcov run
gcov_expected_output="expected_gcov.json"

# Override to change the file that contains the expected output for the lcov run
lcov_expected_output="expected_lcov.json"

gcc_version=$(g++ -v 2>&1 | awk '/gcc version/ {print $3}')
if [[ "$gcc_version" < "5.5" ]]; then
    echo "LEGACY G++ detected: skipping GCOV missing files test"
    modes="lcov"
else
    modes="gcov lcov"
fi
