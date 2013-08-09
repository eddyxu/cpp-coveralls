Upload C/C++ coverage report to coveralls.io
=============

[![Build Status](https://travis-ci.org/eddyxu/cpp-coveralls.png?branch=master)](https://travis-ci.org/eddyxu/cpp-coveralls)

Inspired from [z4r/python-coveralls](https://github.com/z4r/python-coveralls), it uploads the coverage report of C/C++ project to [coveralls.io](https://coveralls.io/)

# Instruction

 * Build your project with [gcov support](http://gcc.gnu.org/onlinedocs/gcc/Gcov.html)
 * Run tests
 * Run `coveralls`

## Usage:

```sh
$ coveralls -h
usage: coveralls [-h] [--gcov FILE] [-r DIR] [-e DIR|FILE] [-x EXT] [-y FILE]
                 [-t TOKEN] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --gcov FILE           set the location of gcov
  -r DIR, --root DIR    set the root directory
  -e DIR|FILE, --exclude DIR|FILE
                        set exclude file or directory
  -x EXT, --extension EXT
                        set extension of files to process
  -y FILE, --coveralls-yaml FILE
                        coveralls yaml file name (default: .coveralls.yml)
  -t TOKEN, --repo_token TOKEN
                        set the repo_token of this project
  --verbose             print verbose messages
```

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
