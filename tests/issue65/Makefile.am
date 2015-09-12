AUTOMAKE_OPTIONS = foreign
ACLOCAL_AMFLAGS = -I m4

CXXFLAGS+=-fprofile-arcs -ftest-coverage -Ilib/src
LDFLAGS+=-fprofile-arcs
LIBS+=-lgcov

bin_PROGRAMS = main
main_SOURCES = test.cpp lib/src/foo.cpp
