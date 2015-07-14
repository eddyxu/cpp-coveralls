#!/bin/bash -ex
#
# Run system test.

coveralls --help

cat > foo.c <<'EOF'
int main() {
    int a = 1;
    if(a == 2) {
        a = 3;
        /* LCOV_EXCL_START */
        a = 4;
        a = 5;
        /* LCOV_EXCL_STOP */
        a = 6;
    }
    if(a == 7) {
        a = 8;
        a = 9; /* LCOV_EXCL_LINE */
    }
    return 0;
}
EOF
gcc -coverage -o foo foo.c
./foo

if [ -z "$TRAVIS_JOB_ID" ]; then
    export COVERALLS_REPO_TOKEN="fake testing token"
fi

coveralls --verbose --encodings utf-8 latin-1 foobar | \
    grep '\[1, 1, 1, 0, None, None, None, None, 0, None, 1, 0, None, None, 1, None\]'
rm -f foo foo.c* foo.gc*
