unused.o: unused.h unused.cpp
	$(CXX) --coverage -c -o unused.o unused.cpp
foo: foo.c unused.o
	$(CXX) --coverage -o foo foo.c

clean:
	rm -f foo *.gcno *.gcda output *.gcov output.json unused.o

prepare_test: foo

test: foo
	./foo
