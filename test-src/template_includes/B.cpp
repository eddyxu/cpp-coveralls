#include "common_header.h"

template class Util <int>;
template class Util <char>;
int main() {
    Util<char> u;
    return (int) u.Method_B(0);
}
