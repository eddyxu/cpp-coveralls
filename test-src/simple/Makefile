foo: foo.c
	gcc --coverage -o foo foo.c

clean:
	rm -f foo *.gcno *.gcda output *.gcov output.json

test: foo
	./foo
