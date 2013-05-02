Upload C++/C coverage report to coveralls.io
=============

[![Build Status](https://travis-ci.org/eddyxu/cpp-coveralls.png?branch=master)](https://travis-ci.org/eddyxu/cpp-coveralls)

Inspired from [z4r/python-coveralls](https://github.com/z4r/python-coveralls), it uploads the coverage report of C/C++ project to [coveralls.io](https://coveralls.io/)


# Instruction

 * Build your project with [gcov support](http://gcc.gnu.org/onlinedocs/gcc/Gcov.html)
 * Run tests
 * Run `coveralls`


## Example `.travis.yml`

```
language: cpp
compiler:
  - gcc
before_install:
  - sudo pip install cpp-coveralls --use-mirrors
script:
  - ./configure --enable-gcov && make && make check
after_success:
  - coveralls --exclude lib --exclude tests
```
