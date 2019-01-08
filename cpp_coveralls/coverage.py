# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2015 (c) Lei Xu <eddyxu@gmail.com>

from __future__ import absolute_import
from builtins import str

import argparse
import hashlib
import io
import os
import re
import subprocess
import sys

from . import gitrepo


_CPP_EXTENSIONS = ['.h', '.hh', '.hpp', '.hxx', '.c', '.cc', '.cpp', '.cxx', '.m', '.mm']
_SKIP_DIRS = set(['.git', '.hg', '.svn', 'deps'])


def create_args(params):
    parser = argparse.ArgumentParser('coveralls')
    parser.add_argument('--verbose', action='store_true',
                        help='print verbose messages')
    parser.add_argument('--dryrun', action='store_true',
                        help='run coveralls without uploading report')
    parser.add_argument('--gcov', metavar='FILE', default='gcov',
                        help='set the location of gcov')
    parser.add_argument('--gcov-options', metavar='GCOV_OPTS', default='',
                        help='set the options given to gcov')
    parser.add_argument('-r', '--root', metavar='DIR', default='.',
                        help='set the root directory')
    parser.add_argument('-b', '--build-root', metavar='DIR',
                        help='set the directory from which gcov will '
                             'be called; by default gcov is run in the '
                             'directory of the .o files; however the paths '
                             'of the sources are often relative to the '
                             'directory from which the compiler was run and '
                             'these relative paths are saved in the .o '
                             'file; when this happens, gcov needs to run in '
                             'the same directory as the compiler in order '
                             'to find the source files')
    parser.add_argument('-e', '--exclude', metavar='DIR|FILE', action='append',
                        help='set exclude file or directory', default=[])
    parser.add_argument('-i', '--include', metavar='DIR|FILE', action='append',
                        help='set include file or directory', default=[])
    parser.add_argument('-E', '--exclude-pattern', dest='regexp',
                        action='append', metavar='REGEXP', default=[],
                        help='set exclude file/directory pattern')
    parser.add_argument('--exclude-lines-pattern',
                        action='append', metavar='REGEXP', default=[],
                        help='set exclude file/directory pattern')
    parser.add_argument('-x', '--extension', metavar='EXT', action='append',
                        help='set extension of files to process')
    parser.add_argument('-y', '--coveralls-yaml', default='.coveralls.yml',
                        metavar='FILE',
                        help='coveralls yaml file name '
                             '(default: .coveralls.yml)')
    parser.add_argument('-n', '--no-gcov', action='store_true', default=False,
                        help='do not run gcov')
    parser.add_argument('-t', '--repo-token', '--repo_token', default='',
                        metavar='TOKEN',
                        help='set the repo_token of this project, '
                             'alternatively you can set the environmental '
                             'variable COVERALLS_REPO_TOKEN')
    parser.add_argument('--encodings',
                        default=['utf-8', 'latin-1'], nargs='+',
                        help='source encodings to try in order of preference '
                             '(default: %(default)s)')
    parser.add_argument('--dump', nargs='?', type=argparse.FileType('w'),
                        help='dump JSON payload to a file',
                        default=None, metavar='FILE')
    parser.add_argument('--follow-symlinks', action='store_true',
                        help='Follow symlinks (default off)')
    parser.add_argument('-l', '--lcov-file', metavar='FILE',
                        help='Upload lcov generated info file')
    parser.add_argument('--max-cov-count', metavar='NUMBER', type=int,
                        help='Max number for line coverage count. If line'
                             'coverage count is greater than the given number'
                             '(Max + 1) will be put instead. Helps in managing'
                             'line coverage count which is higher than max int'
                             'value supported by coveralls.')

    return parser.parse_args(params)


def is_source_file(args, filepath):
    """Returns true if it is a C++ source file."""
    if args.extension:
        return os.path.splitext(filepath)[1] in args.extension
    else:
        return os.path.splitext(filepath)[1] in _CPP_EXTENSIONS


def exclude_paths(args):
    """Returns the absolute paths for excluded path."""
    results = []
    if args.exclude:
        for excl_path in args.exclude:
            results.append(os.path.abspath(os.path.join(args.root, excl_path)))
    return results


_cached_exclude_rules = None


def create_exclude_rules(args):
    """Creates the exlude rules
    """
    global _cached_exclude_rules
    if _cached_exclude_rules is not None:
        return _cached_exclude_rules
    rules = []
    for excl_path in args.exclude:
        abspath = os.path.abspath(os.path.join(args.root, excl_path))
        rules.append((abspath, True))
    for incl_path in args.include:
        abspath = os.path.abspath(os.path.join(args.root, incl_path))
        rules.append((abspath, False))
    _cached_exclude_rules = sorted(rules, key=lambda p: p[0])
    return _cached_exclude_rules


def is_child_dir(parent, child):
    relaive = os.path.relpath(child, parent)
    return not relaive.startswith(os.pardir)


def is_excluded_path(args, filepath):
    """Returns true if the filepath is under the one of the exclude path."""
    # Try regular expressions first.
    for regexp_exclude_path in args.regexp:
        if re.match(regexp_exclude_path, filepath):
            return True
    abspath = os.path.abspath(filepath)
    if args.include:
        # If the file is outside of any include directories.
        out_of_include_dirs = True
        for incl_path in args.include:
            absolute_include_path = os.path.abspath(os.path.join(args.root, incl_path))
            if is_child_dir(absolute_include_path, abspath):
                out_of_include_dirs = False
                break
        if out_of_include_dirs:
            return True

    excl_rules = create_exclude_rules(args)
    for i, rule in enumerate(excl_rules):
        if rule[0] == abspath:
            return rule[1]
        if is_child_dir(rule[0], abspath):
            # continue to try to longest match.
            last_result = rule[1]
            for j in range(i + 1, len(excl_rules)):
                rule_deep = excl_rules[j]
                if not is_child_dir(rule_deep[0], abspath):
                    break
                last_result = rule_deep[1]
            return last_result
    return False


def posix_path(path):
    return path.replace(os.path.sep, '/')


def is_libtool_dir(dir_path):
    return os.path.basename(dir_path) == ".libs"


def libtool_dir_to_source_dir(dir_path):
    return os.path.dirname(dir_path)


def libtool_source_file_path(dir_path, source_file_path):
    source_dir_path = libtool_dir_to_source_dir(dir_path)
    return os.path.join(source_dir_path, source_file_path)


def filter_dirs(root, dirs, excl_paths):
    """Filter directory paths based on the exclusion rules defined in
    'excl_paths'.
    """
    filtered_dirs = []
    for dirpath in dirs:
        abspath = os.path.abspath(os.path.join(root, dirpath))
        if os.path.basename(abspath) in _SKIP_DIRS:
            continue
        if abspath not in excl_paths:
            filtered_dirs.append(dirpath)
    return filtered_dirs


def run_gcov(args):
    excl_paths = exclude_paths(args)
    for root, dirs, files in os.walk(args.root, followlinks=args.follow_symlinks):
        dirs[:] = filter_dirs(root, dirs, excl_paths)

        root_is_libtool_dir = is_libtool_dir(root)
        for filepath in files:
            basename, ext = os.path.splitext(filepath)
            if ext == '.gcno':
                gcov_root = root
                local_gcov_options = ''
                # If the build root is set, run gcov in it, else run gcov in
                # the directories of the .o files.
                gcov_files = []
                custom_gcov_root = args.build_root
                if not custom_gcov_root and root_is_libtool_dir:
                    custom_gcov_root = libtool_dir_to_source_dir(root)
                if custom_gcov_root:
                    gcov_root = custom_gcov_root
                    local_gcov_options = local_gcov_options + \
                        ' --object-directory "%s"' % (os.path.abspath(root))
                    # List current gcov files in build root. We want to move
                    # only the one we will generate now.
                    for files in os.listdir(custom_gcov_root):
                        if files.endswith('.gcov'):
                            gcov_files.append(files)
                if re.search(r".*\.c.*", basename):
                    path = os.path.abspath(os.path.join(root, basename + '.o'))
                    subprocess.call(
                        'cd "%s" && %s %s%s "%s"' % (
                            gcov_root, args.gcov, args.gcov_options, local_gcov_options, path),
                        shell=True)
                else:
                    path = os.path.abspath(os.path.join(root, basename))
                    subprocess.call(
                        'cd "%s" && %s %s%s "%s"' % (
                            gcov_root, args.gcov, args.gcov_options, local_gcov_options, filepath),
                        shell=True)
                # If gcov was run in the build root move the resulting gcov
                # file to the same directory as the .o file.
                if custom_gcov_root:
                    for files in os.listdir(custom_gcov_root):
                        if files.endswith('.gcov') and files not in gcov_files:
                            os.rename(os.path.join(custom_gcov_root, files),
                                      os.path.join(root, files))


def parse_gcov_file(args, fobj, filename):
    """Parses the content of .gcov file
    """
    coverage = []
    ignoring = False
    for line in fobj:
        report_fields = line.decode('utf-8', 'replace').split(':', 2)
        if len(report_fields) == 1:
            continue
        print(report_fields)
        cov_num = report_fields[0].strip()
        if len(line) != 0
            line_num = int(report_fields[1].strip())
            text = report_fields[2]
            if line_num == 0:
                continue
        if re.search(r'\bLCOV_EXCL_START\b', text):
            if ignoring:
                sys.stderr.write("Warning: %s:%d: nested LCOV_EXCL_START, "
                                 "please fix\n" % (filename, line_num))
            ignoring = True
        elif re.search(r'\bLCOV_EXCL_(STOP|END)\b', text):
            if not ignoring:
                sys.stderr.write("Warning: %s:%d: LCOV_EXCL_STOP outside of "
                                 "exclusion zone, please fix\n" % (filename,
                                                                   line_num))
            if 'LCOV_EXCL_END' in text:
                sys.stderr.write("Warning: %s:%d: LCOV_EXCL_STOP is the "
                                 "correct keyword\n" % (filename, line_num))
            ignoring = False
        if cov_num == '-':
            coverage.append(None)
        elif cov_num == '#####':
            # Avoid false positives.
            if (
                ignoring or
                any([re.search(pattern, text) for pattern in args.exclude_lines_pattern])
            ):
                coverage.append(None)
            else:
                coverage.append(0)
        elif cov_num == '=====':
            # This is indicitive of a gcov output parse
            # error.
            coverage.append(0)
        else:
            coverage.append(int(cov_num.rstrip('*')))
    return coverage


def parse_lcov_file_info(args, filepath, line_iter, line_coverage_re, file_end_string):
    """ Parse the file content in lcov info file
    """
    coverage = []
    lines_covered = []
    for line in line_iter:
        if line != "end_of_record":
            line_coverage_match = line_coverage_re.match(line)
            if line_coverage_match:
                line_no = line_coverage_match.group(1)
                cov_count = int(line_coverage_match.group(2))
                if args.max_cov_count:
                    if cov_count > args.max_cov_count:
                        cov_count = args.max_cov_count + 1
                lines_covered.append((line_no, cov_count))
        else:
            break

    num_code_lines = len([line.rstrip('\n') for line in open(filepath, 'r')])
    coverage = [None] * num_code_lines
    for line_covered in lines_covered:
        coverage[int(line_covered[0]) - 1] = line_covered[1]

    return coverage

def combine_reports(original, new):
    """Combines two gcov reports for a file into one by adding the number of hits on each line
    """
    if original is None:
        return new
    report = {}
    report['name'] = original['name']
    report['source_digest'] = original['source_digest']
    coverage = []
    for original_num, new_num in zip(original['coverage'], new['coverage']):
        if original_num is None:
            coverage.append(new_num)
        elif new_num is None:
            coverage.append(original_num)
        else:
            coverage.append(original_num + new_num)

    report['coverage'] = coverage
    return report

def collect_non_report_files(args, discovered_files):
    """Collects the source files that have no coverage reports.
    """
    excl_paths = exclude_paths(args)
    abs_root = os.path.abspath(args.root)
    non_report_files = []
    for root, dirs, files in os.walk(args.root, followlinks=args.follow_symlinks):
        dirs[:] = filter_dirs(root, dirs, excl_paths)

        for filename in files:
            if not is_source_file(args, filename):
                continue
            abs_filepath = os.path.join(os.path.abspath(root), filename)
            if is_excluded_path(args, abs_filepath):
                continue
            filepath = os.path.relpath(abs_filepath, abs_root)
            if filepath not in discovered_files:
                src_report = {}
                src_report['name'] = posix_path(filepath)
                coverage = []
                with io.open(abs_filepath, mode='rb') as fobj:
                    for _ in fobj:
                        coverage.append(None)
                    fobj.seek(0)
                    src_report['source_digest'] = hashlib.md5(fobj.read()).hexdigest()
                src_report['coverage'] = coverage
                non_report_files.append(src_report)
    return non_report_files


def collect(args):
    """Collect coverage reports."""
    excl_paths = exclude_paths(args)

    report = {}
    if args.repo_token:
        report['repo_token'] = args.repo_token

    report['service_name'] = args.service_name
    report['service_job_id'] = args.service_job_id

    if os.getenv('COVERALLS_PARALLEL', False):
        report['parallel'] = 'true'

    args.exclude_lines_pattern.extend([
        r'\bLCOV_EXCL_LINE\b',
        r'^\s*};?\s*$',
        r'^\s*(inline|static)'
        ])

    discovered_files = set()
    src_files = {}
    abs_root = os.path.abspath(args.root)
    if args.lcov_file:
        info_lines = [line.rstrip('\n') for line in open(args.lcov_file, 'r')]
        line_iter = iter(info_lines)
        new_file_re = re.compile('SF:(.*)')
        line_coverage_re = re.compile('DA:(\d+),(\d+)');
        for line in line_iter:
            new_file_match = new_file_re.match(line)
            if new_file_match:
                src_report = {}
                filepath = new_file_match.group(1)
                if args.root:
                    filepath = os.path.relpath(filepath, args.root)
                abs_filepath = os.path.join(abs_root, filepath)
                src_report['name'] = str(posix_path(filepath))
                with io.open(abs_filepath, mode='rb') as src_file:
                    src_report['source_digest'] = hashlib.md5(src_file.read()).hexdigest()
                src_report['coverage'] = parse_lcov_file_info(args, abs_filepath, line_iter, line_coverage_re, "end_of_record")
                src_files[filepath] = src_report
            elif line != "TN:":
                print('Invalid info file')
                print('line: ' + line)
                sys.exit(0)
    else:
        for root, dirs, files in os.walk(args.root, followlinks=args.follow_symlinks):
            dirs[:] = filter_dirs(root, dirs, excl_paths)

            root_is_libtool_dir = is_libtool_dir(root)
            for filepath in files:
                if os.path.splitext(filepath)[1] == '.gcov':
                    gcov_path = os.path.join(os.path.join(root, filepath))
                    with open(gcov_path, mode='rb') as fobj:
                        source_file_line = fobj.readline().decode('utf-8', 'replace')
                        source_file_path = source_file_line.split(':')[-1].strip()
                        if not os.path.isabs(source_file_path):
                            if args.build_root:
                                source_file_path = os.path.join(
                                    args.build_root, source_file_path)
                            elif root_is_libtool_dir:
                                source_file_path = os.path.abspath(
                                    libtool_source_file_path(
                                        root, source_file_path))
                            else:
                                if not source_file_path.startswith(os.path.pardir + os.path.sep) and \
                                        os.path.dirname(source_file_path):
                                    the_root = abs_root
                                else:
                                    the_root = root
                                source_file_path = os.path.abspath(
                                    os.path.join(the_root, source_file_path))
                        src_path = os.path.relpath(source_file_path, abs_root)
                        if src_path.startswith(os.path.pardir + os.path.sep):
                            continue
                        if is_excluded_path(args, source_file_path):
                            continue

                        src_report = {}
                        src_report['name'] = posix_path(src_path)
                        discovered_files.add(src_path)
                        with io.open(source_file_path, mode='rb') as src_file:
                            src_report['source_digest'] = hashlib.md5(src_file.read()).hexdigest()

                        src_report['coverage'] = parse_gcov_file(args, fobj, gcov_path)
                        if src_path in src_files:
                            src_files[src_path] = combine_reports(src_files[src_path], src_report)
                        else:
                            src_files[src_path] = src_report

    report['source_files'] = list(src_files.values())
    # Also collects the source files that have no coverage reports.
    if not args.lcov_file:
        report['source_files'].extend(
            collect_non_report_files(args, discovered_files))

    # Use the root directory to get information on the Git repository
    report['git'] = gitrepo.gitrepo(abs_root)
    return report
