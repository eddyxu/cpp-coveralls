llib/lib.o: llib/lib.cpp llib/lib.h
	$(CXX) --coverage -c -o $@ llib/lib.cpp

llib/lib.a: llib/lib.o
	ar cr $@ $+

A/a: A/a.cpp llib/lib.a
	cd A && $(CXX) --coverage -I../llib -o a a.cpp ../llib/lib.a

B/b: B/b.cpp llib/lib.a
	cd B && $(CXX) --coverage -I../llib -o b b.cpp ../llib/lib.a

prepare_test: A/a B/b

test: prepare_test
	cd A && ./a
	cd B && ./b

clean:
	rm -f llib/lib.o llib/lib.a A/a B/b A/a.gc* B/b.gc* llib/lib.*gc* lcov.info
