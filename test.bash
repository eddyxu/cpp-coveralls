#!/bin/bash -ex
#
# Run system test.

coveralls --help

echo 'int main() {return 0;}' > foo.c
gcc -coverage -o foo foo.c
./foo
coveralls --verbose --encodings utf-8 latin-1 foobar | \
    grep 'coverage' | grep '1'
rm -f foo foo.c* foo.gc*
