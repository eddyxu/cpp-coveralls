SOURCE_TREE=../source_tree
INCLUDE_FLAGS=-I$(SOURCE_TREE)/llib

lib.o: $(SOURCE_TREE)/llib/lib.cpp $(SOURCE_TREE)/llib/lib.h
	g++ --coverage -c -o $@ $(SOURCE_TREE)/llib/lib.cpp

lib.a: lib.o
	ar cr $@ $+

a: $(SOURCE_TREE)/A/a.cpp lib.a
	g++ --coverage $(INCLUDE_FLAGS) -o a $+

b: $(SOURCE_TREE)/B/b.cpp lib.a
	g++ --coverage $(INCLUDE_FLAGS) -o b $+

prepare_test: a b

test: prepare_test
	./a
	./b

clean:
	rm -f lib.o lib.a a b a.gc* b.gc* lib.gc* lcov.info
