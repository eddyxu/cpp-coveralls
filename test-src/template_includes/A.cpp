#include "common_header.h"

template class Util <int>;
template class Util <char>;
int main() {
    Util<int> u;
    return u.Method_A(0);
}
