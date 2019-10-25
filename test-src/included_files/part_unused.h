void unused_f(int& i);
void g(int& i);

struct Inline {
    void inline_unused_f(int& i) { i*=2; }
    void inline_g(int& i) { i*=2; }
};
