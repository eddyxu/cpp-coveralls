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
