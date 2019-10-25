A: A.cpp common_header.h
	g++ --coverage -o A A.cpp

B: B.cpp common_header.h
	g++ --coverage -o B B.cpp

clean:
	rm -f B A *.gcno *.gcda output *.gcov output.json *.gch

prepare_test: A B

test: prepare_test
	./A
	./B
