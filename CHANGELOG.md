Version 0.3.9 (June 21th, 2014)
  * Add the follow-symlinks option to the remaining os.walk calls. (#90 by @nomis52)

Version 0.3.8 (June 20th, 2015)
  * Fix typo (#87 by @Oxced)
  * Add an option to follow symlinks (#89 by @nomis52)

Version 0.3.7 (May 10th, 2015)
  * Add Objective-C file extensions by default. (#86 by @0xced)
  * Properly quote paths when invoking shell (#85 by @0xced)
  * Cpp-coverals will now raise an exception if neither the travis job id nor the repo token are found (#84 by @mkfifo)

Version 0.3.6 (April 17th, 2015)
  * Use new coveralls API `source_digest` instead of `source`. (#83 by @dmakarov)

Version 0.3.5 (April 15th, 2015)
  * cpp-coveralls now respects environmental variable `COVERALLS_REPO_TOKEN` (#78 by @mkfifo)

Version 0.3.4 (March 23th, 2015)
  * Skip over messages in gcov file. (#74 by @DaMouse404)
  * Added additional configuration settings to the .coveralls.yaml file (#75 by @umar456)

Version 0.3.3 (February 3rd, 2015)
  * Support recursive include and exclude rules. (by @eddyxu)

Version 0.3.2 (January 18th, 2015)
  * Support excluding files in the include directories. (by @eddyxu)

Version 0.3.1 (November 3rd, 2014)
  * Added support for directories using the include option. (#68 by @jbenden)

Version 0.3.0 (November 2nd, 2014)
  * Added option to include specific files. (#67 by @jbenden)

Version 0.2.9 (August 20th, 2014)
  * Fixed ignore lines in source code. (#63 by @remram44)

Version 0.2.8 (July 12th, 2014)
  * Ignore incorrectly reported lines (#60 by @myint)

Version 0.2.7 (May 24th, 2014)
  * Fixed a bug caused by debug info (#59 by eddyxu)

Version 0.2.6 (May 24th, 2014)
  * Allow to parse file through relative path (#58 by eddyxu)

Version 0.2.5 (May 19th, 2014)
  * Prevent cluttering gcov-options with local options (#53 by @ptomulik)

Version 0.2.4 (May 17th, 2014)
  * Combine multiple source files if they have the same path (#52 by @worktycho)

Version 0.2.3 (May 4th, 2014)
  * Fix source file path generation (#47 by sjaeckel)

Version 0.2.2 (May 2nd, 2014)
  * Fixed a source file path generation problem (#41 by @sjaeckel)
  * Enable testing on Python 3.4 (#44 by @myint)
  * Support trying multiple encodings (#45 by @myint)

Version 0.2.1 (April 23th, 2014)
  * Add more C++ extensions and ignore Mercurial directory. Also fix a FileNotFoundError (#39 by @bchretien)
  * Fix Git repository for report (use root directory). (#40 by @bchretien)

Version 0.2.0 (April 16th, 2014)
  * Remove `--use-mirrors` in README (#37 by @myint)
  * Move module name from coveralls to cpp_coveralls (avoid name clash with
	other languages' coverells script) (#38 by @anjos)

Version 0.1.7 (April 8th, 2014)
  * Added an alias `cpp-coveralls` to support using it for multiple languages. (#35)
  * Added `--dump` parameter to write JSON payload to output file instead of uploading to coveralls.(#35)

Version 0.1.6 (April 6th, 2014)
  * Added a `--dryrun` parameter (#36)
  * Fixed a typo in OS X instructions (#34 by @myint)

Version 0.1.5 (March 9th, 2014)
  * Respect "LCOV_EXCL_LINE" exclusions (#30 by @myint)
  * Added MacOSX special instructions in README (#27,#28 by @MartinDelille)
  * Fix file extension for `.c` file (#25 by @kt3k)

Version 0.1.4 (Jan 26th, 2014)
  * Support GNU Libtool (#23 by @kou)

Version 0.1.3 (Jan 19th, 2014)
  * Update USAGE in README.md
  * FIXED: Filter paths consistently for executed and unexecuted files. (#19,#20,#21 by @smspillaz)

Version 0.1.2 (Dec 7th, 2013)
  * Allow specifying encoding from command line (#17 by @myint)
  * Added `--repo-token` for consistency (#17 by @myint)
  * Format to follow PEP8 and use relative imports (#17 by @myint)

Version 0.1.1 (Dec 2nd, 2013)
  * Fixed unused argument (#16 by @myint)

Version 0.1.0 (Oct 21th, 2013)
  * Enable the use of a build directory and add access to gcov options (#14 by @nharraud)

Version 0.0.9 (Oct 1st, 2013)
  * Add `-n/--no-gcov` parameter to disable running `gcov` by coveralls (#13)
  * Add `-E/--exclude-pattern` to support use regular expression as exclude rules. (#12)

Version 0.0.8 (Sep 3th, 2013)
  * Skip '.libs' and '.deps' directories (#11 by @nijel)

Version 0.0.7 (Aug 06th, 2013)
  * Allow specifying which extensions should be considered as C/CPP files (#7 by @tbonfort)
  * Treat git output as UTF-8 (#9 by @czchen)

Version 0.0.6 (July 16th, 2013)
  * Adapt coverage.py script to work with cmake project (#5 by @meshell)
