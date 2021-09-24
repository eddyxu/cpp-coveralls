#!/bin/bash
#
# Run system test.

export PATH="$PATH:$PWD/test-utils"

exit_on_fail="no"

function ParseArguments {
    while [[ "$1" != "" ]]; do
        if [[ "$1" == "-e" || "$1" == "--exit-on-fail" ]]; then
            exit_on_fail="yes"
        fi
        shift
    done
}

failed_tests=0
function TestFailed {
    let "failed_tests+=1"
    if [[ "$exit_on_fail" == "yes" ]]; then
        echo "(-e): Exiting due to first failure"
        exit 1
    fi
}

ParseArguments $@

testDir.sh $@ test-src/simple || TestFailed
testDir.sh $@ test-src/included_files || TestFailed
testDir.sh $@ test-src/excluded_files || TestFailed
testDir.sh $@ test-src/static_lib || TestFailed
testDir.sh $@ test-src/out_of_tree  || TestFailed
testDir.sh $@ test-src/missing_files  || TestFailed
testDir.sh $@ test-src/template_includes/ || TestFailed

if [[ $failed_tests -gt 0 ]]; then
    echo ""
    echo "FAIL: $failed_tests unexpected failures!"
fi

exit $failed_tests
