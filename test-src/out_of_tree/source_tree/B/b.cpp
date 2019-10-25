#include "lib.h"

int main() {
    int ret = 0;
    tripple_it(ret);
    inline_double id;
    id.g(ret);
    return ret;
}
