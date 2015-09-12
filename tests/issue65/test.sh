#!/bin/sh

GCOV=${GCOV:=gcov}

set -e

mkdir -p m4
aclocal -I m4 --install
autoreconf --install --verbose --force --warnings=all
automake --add-missing --copy
./configure
make
./main

coveralls --gcov ${GCOV} --dryrun
