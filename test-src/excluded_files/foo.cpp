#include "part_unused.h"
#include "extra_lib/toy.h"
#include "another_extra_lib/another_toy.h"

int main() {
    int a = 1;
    g(a);
    Inline i;
    i.inline_g(a);
    toy(a);
    a_toy(a);
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
