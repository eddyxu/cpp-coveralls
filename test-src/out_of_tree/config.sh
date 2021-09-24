#!/bin/bash

# Set if we expect the GCOV test for a known reason
gcov_fail_reason=""

# We must invoke "make" in the build tree
build_dir="build_tree"



# lcov must be invoked in the build-tree, which means we must:
#    -> tell lcov where the source tree is 
#    -> tell coveralls to strip the "../source_tree prefix off of
#       the paths
lcov_dir="build_tree"
lcov_coveralls_dir="build_tree"
lcov_coveralls_flags="--root .."
lcov_flags="-b ../source_tree"


