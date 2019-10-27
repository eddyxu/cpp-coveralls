foo: foo.c
	$(CXX) --coverage -o foo foo.c

clean:
	rm -f foo *.gcno *.gcda output *.gcov output.json

prepare_test: foo

test: prepare_test
	./foo
