Upload C/C++ coverage report to coveralls.io
=============

[![Build Status](https://travis-ci.org/eddyxu/cpp-coveralls.png?branch=master)](https://travis-ci.org/eddyxu/cpp-coveralls) [![Code Quality](https://landscape.io/github/eddyxu/cpp-coveralls/master/landscape.png)](https://landscape.io/github/eddyxu/cpp-coveralls/master)

Inspired from [z4r/python-coveralls](https://github.com/z4r/python-coveralls), it uploads the coverage report of C/C++ project to [coveralls.io](https://coveralls.io/)

# Instruction

 * Build your project with [gcov support](http://gcc.gnu.org/onlinedocs/gcc/Gcov.html)
 * Run tests
 * Run `coveralls`

## Usage:

```sh
$ coveralls -h
usage: coveralls [-h] [--gcov FILE] [--gcov-options GCOV_OPTS] [-r DIR]
                 [-b DIR] [-e DIR|FILE] [-E REGEXP] [-x EXT] [-y FILE] [-n]
                 [-t TOKEN] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --gcov FILE           set the location of gcov
  --gcov-options GCOV_OPTS
                        set the options given to gcov
  -r DIR, --root DIR    set the root directory
  -b DIR, --build-root DIR
                        set the directory from which gcov will be called. By
                        default gcov is run in the directory of the .o files.
                        However the paths of the sources are often relative to
                        the directory from which the compiler was run and
                        these relative paths are saved in the .o file. When
                        this happens, gcov needs to run in the same directory
                        as the compiler in order to find the source files.
  -e DIR|FILE, --exclude DIR|FILE
                        set exclude file or directory
  -E REGEXP, --exclude-pattern REGEXP
                        set exclude file/directory pattern
  -x EXT, --extension EXT
                        set extension of files to process
  -y FILE, --coveralls-yaml FILE
                        coveralls yaml file name (default: .coveralls.yml)
  -n, --no-gcov         do not run gcov.
  -t TOKEN, --repo-token TOKEN, --repo_token TOKEN
						set the repo_token of this project
  --encoding ENCODING   source encoding (default: utf-8)
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
