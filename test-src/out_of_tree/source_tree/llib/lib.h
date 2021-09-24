void double_it(int& i);

void tripple_it(int& i);

struct inline_double {
    void f(int& i) { i*=2; }
    void g(int& i) { i*=2; }
};
