#!/bin/bash -ex
#
# Run system test.

echo 'int main() {return 0;}' > foo.c
gcc -coverage -o foo foo.c
./foo
coveralls --verbose | grep 'coverage' | grep '1'
rm -f foo foo.c* foo.gc*
