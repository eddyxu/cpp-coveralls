part_unused.o: part_unused.h part_unused.cpp
	g++ --coverage -c -o part_unused.o part_unused.cpp

toy.o: extra_lib/toy.cpp extra_lib/toy.h
	g++ --coverage -c -o toy.o extra_lib/toy.cpp

a_toy.o: another_extra_lib/another_toy.cpp another_extra_lib/another_toy.h
	g++ --coverage -c -o a_toy.o another_extra_lib/another_toy.cpp

foo: foo.cpp part_unused.o toy.o a_toy.o extra_lib/toy.h another_extra_lib/another_toy.h
	g++ --coverage -o foo foo.cpp part_unused.o toy.o a_toy.o

clean:
	rm -f foo *.gcno *.gcda output *.gcov output.json part_unused.o toy.o a_toy.o

prepare_test: foo

test: foo
	./foo
