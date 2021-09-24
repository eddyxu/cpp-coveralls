#!/bin/bash

gcc_versions=""
default_gcc_versions="4.8 5 6 7 8 9"

# START: Valid config.sh options
#    The following variables can be set in the directory's config.sh file

# Set if we expect the GCOV test for a known reason
gcov_fail_reason=""

# Set if we expect the LCOV test for a known reason
lcov_fail_reason=""

# Modes to test in (default "gcov lcov")
#
modes="gcov lcov"

# Set to override the build directory (default is the test's root directory).
# This is where "make" will be invoked.
# Path should relative to the test's root directory
build_dir=""

# Set to provide additional flags to cpp-coveralls when in gcov mode
gcov_coveralls_flags=""

# Set to provide additional flags to cpp-coveralls when in lcov mode
lcov_coveralls_flags=""

# Set to provide additional flags lcov on every invocation
lcov_flags=""

# Set to override the directory in which lcov will be invoked
# (default is the tests's root directory)
# Path should relative to the test's root directory
lcov_dir=""

# Set to override the directory in which cpp-coveralls will be invoked
# for gcov (default is the tests's root directory)
# Path should relative to the test's root directory
gcov_coveralls_dir=""

# Set to override the directory in which cpp-coveralls will be invoked
# for lcov (default is the tests's root directory)
# Path should relative to the test's root directory
lcov_coveralls_dir=""

# Override to change the file that contains the expected output for the gcov run
gcov_expected_output="expected.json"

# Override to change the file that contains the expected output for the lcov run
lcov_expected_output="expected.json"

#
# END: Valid config.sh options
#

# Internal counter of failed tests
failed_tests=0
exit_on_fail="no"


function Usage {
    echo "testDir.sh [-e/ --exit-on-fail] [--gcc-version <version>] test-src/<dir to test>"
    echo ""
    echo "Options:"
    echo "   -e / --exit-on-fail: Stop execution at the first unexpected failure."
    echo "   --gcc_version      : Version of gcc to test (e.g 5 for g++-5 / gcov-5)"
    echo "                        (May be specified multiple times)"
    echo "                        By default the following versions are tested: $default_gcc_versions"
}

#
#  Parse the command line arguments
#
#  Arguments:
#     @: The set of arguments parsed to this script
#
function ParseArguments {
    done="no"
    while [[ "$done" != "yes" ]]; do
        if [[ "$1" == "-e" || "$1" == "--exit-on-fail" ]]; then
            exit_on_fail="yes"
            shift
        elif [[ "$1" == "--gcc-version" ]]; then
            gcc_versions+=" $2"
            shift
            shift
        else
            done="yes"
        fi
    done

    if [[ "$gcc_versions" == "" ]]; then
        gcc_versions=$default_gcc_versions
    fi


    test_dir=$1

    if [[ "$test_dir" == "" || ! -d "$test_dir" ]]; then
        echo "Cannot find test directory: $test_dir"
        Usage
        exit 1
    else
        # hack to get the absolute path
        pushd $test_dir > /dev/null || exit 1
        test_dir=$PWD
        popd > /dev/null || exit 1
    fi
}

function SetupEnvironment {
    gcc_version=$1

    export CXX="g++-$gcc_version"
    export GCOV="gcov-$gcc_version"

    if [ -z "$TRAVIS_JOB_ID" ]; then
        export COVERALLS_REPO_TOKEN="fake testing token"
    fi

    cd $test_dir || exit

    if [[ -e config.sh ]]; then
        source config.sh
    fi

    if [[ ! -e $gcov_expected_output ]]; then
        echo "Cannot test $PWD:"
        echo "    Configured GCOV output file not found ($gcov_expected_output)"
        exit 1
    fi

    if [[ ! -e $lcov_expected_output ]]; then
        echo "Cannot test $PWD:"
        echo "    Configured LCOV output file not found ($lcov_expected_output)"
        exit 1
    fi

    if [[ "$build_dir" != "" && ! -d "$build_dir" ]]; then
        echo "Cannot test $PWD:"
        echo "    No such build directory (build_dir): $build_dir"
        exit 1
    fi

    if [[ "$gcov_coveralls_dir" != "" && ! -d "$gcov_coveralls_dir" ]]; then
        echo "Cannot test $PWD:"
        echo "    No such directory (gcov_coveralls_dir): $gcov_coveralls_dir"
        exit 1
    fi

    if [[ "$lcov_coveralls_dir" != "" && ! -d "$lcov_coveralls_dir" ]]; then
        echo "Cannot test $PWD:"
        echo "    No such directory (lcov_coveralls_dir): $lcov_coveralls_dir"
        exit 1
    fi

    if [[ "$lcov_dir" != "" && ! -d "$lcov_dir" ]]; then
        echo "Cannot test $PWD:"
        echo "    No such directory (lcov_dir): $lcov_dir"
        exit 1
    fi

    if [[ ! -e "$PWD/$build_dir/Makefile" ]]; then
        echo "$PWD/$build_dir does not contain a valid Makefile!"
        Usage
        exit 1
    fi
}

#
#  Check the coveralls result matches the directory's expected.json
#
#  Arguments:
#     1: log           - The logfile to append check result
#     2: expected_json - The filename that contains the json block with the
#                        expected coverage output
#     3: fail_reason   - Set if we expect this to test fail, with a reason text
#
function CheckResult {
    log=$1
    expected_json=$2
    fail_reason=$3

    result=$(check_output.py -e $expected_json)
    failed="no"
    if [[ "$result" != "" ]]; then
        if [[ "$fail_reason" != "" ]]; then
            echo "FAIL (as expected: $fail_reason)" | tee -a $log
        else
            failed="yes"
            echo "FAIL" | tee -a $log
            echo "$result" | sed -e 's/^/   /' | tee -a $log
            echo "   Expected:" | tee -a $log
            cat $expected_json | sed -e 's/^/        /' | tee -a $log
            echo "    Actual Output:" | tee -a $log
            cat output.json | sed -e 's/^/        /' | tee -a $log
            echo
        fi
    else
        if [[ "$fail_reason" != "" ]]; then
            echo "ERROR: PASS (should have failed: $fail_reason)" | tee -a $log
            failed="yes"
        else
            echo "PASS" | tee -a $log
        fi
    fi

    if [[ "$failed" == "yes" ]]; then
        let "failed_tests+=1"
        if [[ "$exit_on_fail" == "yes" ]]; then
            exit 1
        fi
    fi
}

function Make {
    log_file=$1
    shift

    if [[ "$build_dir" != "" ]]; then
        pushd $build_dir >> $log_file
    fi

    echo ">> make $@" >> $log_file
    make $@  >> $log_file 2>&1 || Exit "make command failed!" $log_file

    if [[ "$build_dir" != "" ]]; then
        popd >> $log_file
    fi
}

function CppCoverals {
    log_file=$1
    coveralls_dir=$2
    shift
    shift

    if [[ "$coveralls_dir" != "" ]]; then
        pushd $coveralls_dir >> $log_file
    fi

    echo ">> cpp-coveralls $@" >> $log_file
    cpp-coveralls $@ >> $logfile 2>&1 || Exit "cpp-coveralls failed" "$log_file"

    if [[ "$coveralls_dir" != "" ]]; then
        popd >> $log_file
    fi
}

function LCov {
    log_file=$1
    shift

    if [[ "$lcov_dir" != "" ]]; then
        pushd $lcov_dir >> $log_file
    fi

    echo ">> lcov $lcov_flags $@" >> $log_file
    lcov $lcov_flags $@ >> $log_file 2>&1 || Exit "LCov invocation failed" "$logfile"

    if [[ "$lcov_dir" != "" ]]; then
        popd >> $log_file
    fi
}

function Exit {
    reason=$1
    logfile=$2
    echo "FATAL_ERROR: $reason"
    echo "Test output:"
    cat $logfile | sed -e 's/^/    /'
    exit 1
}


#
#  Test the directory by asking coveralls to do a full gcov run
#
#  Arguments: None
#
function CheckGCOV {
    echo -n ">> Checking $PWD using GCOV (CXX:$CXX, GCOV:$GCOV)..."

    logfile="$PWD/gcov_test_output_$gcc_version"
    CleanUp  > $logfile 2>&1

    Make $logfile test

    CppCoverals $logfile "$gcov_coveralls_dir" --gcov $GCOV --gcov-options '\-lp' --dump $PWD/output.json --verbose  $gcov_coveralls_flags

    CheckResult $logfile "$gcov_expected_output" "$gcov_fail_reason"

    CleanUp
}

#
#  Test the directory by manually running lcov, and asking coveralls to parse the output
#
#  Arguments: None
#
function CheckLCOV {
    echo -n ">> Checking $PWD using LCOV (CXX:$CXX, GCOV:$GCOV)..."

    logfile="$PWD/lcov_test_output_$gcc_version"
    CleanUp  > $logfile 2>&1

    Make $logfile prepare_test

    LCov $logfile --gcov-tool "$GCOV" --capture -d . -i --output-file="$PWD/lcov_baseline.info"

    Make $logfile test

    LCov $logfile --gcov-tool "$GCOV" --capture -d . --output-file="$PWD/lcov_test_run.info"

    LCov $logfile --gcov-tool "$GCOV" $lcov_flags -a $PWD/lcov_baseline.info -a $PWD/lcov_test_run.info -o "$PWD/lcov.info"

    CppCoverals $logfile "$lcov_coveralls_dir" --dump $PWD/output.json --no-gcov --lcov-file="$PWD/lcov.info" $lcov_coveralls_flags

    CheckResult $logfile "$lcov_expected_output" "$lcov_fail_reason"

    CleanUp
}

#
#  Clean down the current directory, ready to start a new test
#
#  Arguments: None
#
function CleanUp {
    Make /dev/null clean
    rm -f *.gcda *.gcno lcov*.info output.json > /dev/null
    find . -name "*.gcov" | xargs rm -f > /dev/null
}

ParseArguments $@

for v in $gcc_versions; do
    SetupEnvironment $v

    for mode in $modes; do
        if [[ "$mode" == "gcov" ]]; then
            CheckGCOV
        elif [[ "$mode" == "lcov" ]]; then
            CheckLCOV
        else
            Exit /dev/stdout "Unknown test mode requested: $mode"
        fi
    done
done

exit $failed_tests
