#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.40])
AC_INIT([FULL-PACKAGE-NAME], [VERSION], [BUG-REPORT-ADDRESS])

AC_CONFIG_HEADERS([config.h])
AC_CONFIG_SRCDIR([test.cpp])
AM_INIT_AUTOMAKE([subdir-objects])

# Checks for programs.
AC_PROG_INSTALL
AC_PROG_MAKE_SET

AC_PROG_CXX
AC_PROG_CC
AC_PROG_LIBTOOL
AC_PROG_RANLIB
LT_INIT
AC_LANG([C++])

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.
CXXFLAGS="$CXXFLAGS -fprofile-arcs -ftest-coverage --coverage"
LDFLAGS="$LDFLAGS -fprofile-arcs"
LIBS="$LIBS -lgcov"

AC_SUBST(CXXFLAGS)
AC_SUBST(LDFLAGS)
AC_SUBST(LIBS)

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
