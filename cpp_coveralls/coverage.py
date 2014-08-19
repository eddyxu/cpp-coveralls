# Copyright 2014 (c) Lei Xu <eddyxu@gmail.com>

from __future__ import absolute_import

import argparse
import contextlib
import io
import os
import re
import subprocess
import sys

from . import gitrepo


_CPP_EXTENSIONS = ['.h', '.hh', '.hpp', '.hxx', '.c', '.cc', '.cpp', '.cxx']
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
                        help='set exclude file or directory')
    parser.add_argument('-E', '--exclude-pattern', dest='regexp',
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
                        help='set the repo_token of this project')
    parser.add_argument('--encodings',
                        default=['utf-8', 'latin-1'], nargs='+',
                        help='source encodings to try in order of preference '
                             '(default: %(default)s)')
    parser.add_argument('--dump', nargs='?', type=argparse.FileType('w'),
                        help='dump JSON payload to a file',
                        default=None, metavar='FILE')

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


def is_excluded_path(args, filepath):
    """Returns true if the filepath is under the one of the exclude path."""
    excl_paths = exclude_paths(args)
    # Try regular expressions first.
    for regexp_exclude_path in args.regexp:
        if re.match(regexp_exclude_path, filepath):
            return True
    abspath = os.path.abspath(filepath)
    for excluded_path in excl_paths:
        if os.path.isdir(excluded_path):
            relpath = os.path.relpath(abspath, excluded_path)
            if len(relpath) > 3 and relpath[:3] != '../':
                return True
        else:
            absexcludefile = os.path.abspath(excluded_path)
            if absexcludefile == abspath:
                return True
    return False


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
    for root, dirs, files in os.walk(args.root):
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
                        ' --object-directory ' + os.path.abspath(root)
                    # List current gcov files in build root. We want to move
                    # only the one we will generate now.
                    for files in os.listdir(custom_gcov_root):
                        if files.endswith('.gcov'):
                            gcov_files.append(files)
                if re.search(r".*\.c.*", basename):
                    path = os.path.abspath(os.path.join(root, basename + '.o'))
                    subprocess.call(
                        'cd %s && %s %s%s %s' % (
                            gcov_root, args.gcov, args.gcov_options, local_gcov_options, path),
                        shell=True)
                else:
                    path = os.path.abspath(os.path.join(root, basename))
                    subprocess.call(
                        'cd %s && %s %s%s %s' % (
                            gcov_root, args.gcov, args.gcov_options, local_gcov_options, filepath),
                        shell=True)
                # If gcov was run in the build root move the resulting gcov
                # file to the same directory as the .o file.
                if custom_gcov_root:
                    for files in os.listdir(custom_gcov_root):
                        if files.endswith('.gcov') and files not in gcov_files:
                            os.rename(os.path.join(custom_gcov_root, files),
                                      os.path.join(root, files))


def parse_gcov_file(fobj, filename):
    """Parses the content of .gcov file
    """
    coverage = []
    ignoring = False
    for line in fobj:
        report_fields = line.split(':')
        cov_num = report_fields[0].strip()
        line_num = int(report_fields[1].strip())
        text = report_fields[2]
        if line_num == 0:
            continue
        if re.search(r'\bLCOV_EXCL_START\b', text):
            if ignoring:
                sys.stderr.write("Warning: %s:%d: nested LCOV_EXCL_START, "
                                 "please fix\n" % (filename, line_num))
            ignoring = True
        elif re.search(r'\bLCOV_EXCL_END\b', text):
            if not ignoring:
                sys.stderr.write("Warning: %s:%d: LCOV_EXCL_END outside of "
                                 "exclusion zone, please fix\n" % (filename,
                                                                   line_num))
            ignoring = False
        if cov_num == '-':
            coverage.append(None)
        elif cov_num == '#####':
            # Avoid false positives.
            if (
                ignoring or
                text.lstrip().startswith(('inline', 'static')) or
                text.strip() == '}' or
                re.search(r'\bLCOV_EXCL_LINE\b', text)
            ):
                coverage.append(None)
            else:
                coverage.append(0)
        elif cov_num == '=====':
            # This is indicitive of a gcov output parse
            # error.
            coverage.append(0)
        else:
            coverage.append(int(cov_num))
    return coverage

def combine_reports(original, new):
    """Combines two gcov reports for a file into one by adding the number of hits on each line
    """
    if original == None:
        return new
    report = {}
    report['name'] = original['name']
    report['source'] = original['source']
    coverage = []
    for original_num, new_num in zip(original['coverage'], new['coverage']):
        if original_num == None:
            coverage.append(new_num)
        elif new_num == None:
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
    for root, dirs, files in os.walk(args.root):
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
                src_report['name'] = filepath
                coverage = []
                with open_with_encodings(abs_filepath,
                                         encodings=args.encodings) as fobj:
                    for _ in fobj:
                        coverage.append(None)
                    fobj.seek(0)
                    src_report['source'] = fobj.read()
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

    discovered_files = set()
    src_files = {}
    abs_root = os.path.abspath(args.root)
    for root, dirs, files in os.walk(args.root):
        dirs[:] = filter_dirs(root, dirs, excl_paths)

        root_is_libtool_dir = is_libtool_dir(root)
        for filepath in files:
            if os.path.splitext(filepath)[1] == '.gcov':
                gcov_path = os.path.join(os.path.join(root, filepath))
                with open(gcov_path) as fobj:
                    source_file_line = fobj.readline()
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
                            if not source_file_path.startswith('../') and \
                                    os.path.dirname(source_file_path):
                                the_root = abs_root
                            else:
                                the_root = root
                            source_file_path = os.path.abspath(
                                os.path.join(the_root, source_file_path))
                    src_path = os.path.relpath(source_file_path, abs_root)
                    if len(src_path) > 3 and src_path.startswith('../'):
                        continue
                    if is_excluded_path(args, source_file_path):
                        continue

                    src_report = {}
                    src_report['name'] = src_path
                    discovered_files.add(src_path)
                    with open_with_encodings(
                            source_file_path,
                            encodings=args.encodings) as src_file:
                        src_report['source'] = src_file.read()

                    src_report['coverage'] = parse_gcov_file(fobj, gcov_path)
                    if src_path in src_files:
                        src_files[src_path] = combine_reports(src_files[src_path], src_report)
                    else:
                        src_files[src_path] = src_report

    report['source_files'] = list(src_files.values())
    # Also collects the source files that have no coverage reports.
    report['source_files'].extend(
        collect_non_report_files(args, discovered_files))

    # Use the root directory to get information on the Git repository
    report['git'] = gitrepo.gitrepo(abs_root)
    return report


@contextlib.contextmanager
def open_with_encodings(filename, encodings):
    """Try opening file with various encodings until it works.

    Return the open file.

    """
    with io.open(filename,
                 encoding=try_encodings(filename, encodings)) as input_file:
        yield input_file


def try_encodings(filename, encodings):
    """Try opening file with various encodings and return the one works.

    If none work, raise a ValueError.

    """
    assert encodings

    for current in encodings:
        try:
            with io.open(filename, encoding=current) as input_file:
                input_file.read()
            return current
        except UnicodeDecodeError:
            pass

    raise ValueError(
        'Encodings {encodings} are not compatible with {filename}'.format(
            encodings=encodings,
            filename=filename))
