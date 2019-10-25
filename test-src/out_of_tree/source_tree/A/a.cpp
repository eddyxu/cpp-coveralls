#include "lib.h"

int main() {
    int ret = 0;
    double_it(ret);
    inline_double id;
    id.f(ret);
    return ret;
}
