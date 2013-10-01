# Copyright 2013 (c) Lei Xu <eddyxu@gmail.com>

import os
import subprocess
import re
from coveralls import gitrepo
import argparse


_CPP_EXTENSIONS = ['.h', '.hpp', '.cpp', '.cc', 'c']

def create_args(params):
    parser = argparse.ArgumentParser('coveralls')
    parser.add_argument('--gcov', metavar='FILE', default='gcov',
                        help='set the location of gcov')
    parser.add_argument('-r', '--root', metavar='DIR', default='.',
                        help='set the root directory')
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
                        help='do not run gcov.')
    parser.add_argument('-t', '--repo_token', default='', metavar='TOKEN',
                        help='set the repo_token of this project')
    parser.add_argument('--verbose', action='store_true',
                        help='print verbose messages')
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
    """Returns true if the filepath is under the one of the exclude path
    """
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


def run_gcov(args):
    excl_paths = exclude_paths(args)
    for root, dirs, files in os.walk(args.root):
        filtered_dirs = []
        for dirpath in dirs:
            abspath = os.path.abspath(os.path.join(root, dirpath))
            if not abspath in excl_paths:
                filtered_dirs.append(dirpath)
        dirs[:] = filtered_dirs
        for filepath in files:
            basename, ext = os.path.splitext(filepath)
            if ext == '.gcno':
                if re.search(r".*\.c.*", basename):
                    subprocess.call(
                        'cd %s && %s %s.o' % (root, args.gcov, basename),
                        shell=True)
                else:
                    subprocess.call(
                        'cd %s && %s %s' % (root, args.gcov, basename),
                        shell=True)


def collect(args):
    """Collect coverage reports."""
    excl_paths = exclude_paths(args)
    skip_dirs = set(['.git', '.svn', '.libs', '.deps'])

    report = {}
    if args.repo_token:
        report['repo_token'] = args.repo_token
    report['service_name'] = args.service_name
    report['service_job_id'] = args.service_job_id

    discoverd_files = set()
    report['source_files'] = []
    abs_root = os.path.abspath(args.root)
    for root, dirs, files in os.walk(args.root):
        filtered_dirs = []
        for dirpath in dirs:
            abspath = os.path.abspath(os.path.join(root, dirpath))
            if os.path.basename(abspath) in skip_dirs:
                continue
            if not abspath in excl_paths:
                filtered_dirs.append(dirpath)
        dirs[:] = filtered_dirs

        for filepath in files:
            if os.path.splitext(filepath)[1] == '.gcov':
                gcov_path = os.path.join(os.path.join(root, filepath))
                with open(gcov_path) as fobj:
                    source_file_line = fobj.readline()
                    source_file_path = source_file_line.split(':')[-1].strip()
                    if not os.path.isabs(source_file_path):
                        source_file_path = os.path.abspath(
                            os.path.join(root, source_file_path))
                    src_path = os.path.relpath(source_file_path, abs_root)
                    if len(src_path) > 3 and src_path[:3] == '../':
                        continue
                    if is_excluded_path(args, source_file_path):
                        continue

                    src_report = {}
                    src_report['name'] = src_path
                    discoverd_files.add(src_path)
                    with open(src_path) as src_file:
                        src_report['source'] = src_file.read()

                    coverage = []
                    for line in fobj:
                        report_fields = line.split(':')
                        cov_num = report_fields[0].strip()
                        line_num = int(report_fields[1].strip())
                        text = report_fields[2]
                        if line_num == 0:
                            continue
                        if cov_num == '-':
                            coverage.append(None)
                        elif cov_num == '#####':
                            # Avoid false positives.
                            if (text.lstrip().startswith('static') or
                                    text.strip() == '}'):
                                coverage.append(None)
                            else:
                                coverage.append(0)
                        elif cov_num == '=====':
                            # This is indicitive of a gcov output parse
                            # error.
                            coverage.append(0)
                        else:
                            coverage.append(int(cov_num))
                src_report['coverage'] = coverage
                report['source_files'].append(src_report)

    # Also collects the source files that have no coverage reports.
    for root, dirs, files in os.walk(args.root):
        filtered_dirs = []
        for dirpath in dirs:
            abspath = os.path.abspath(os.path.join(root, dirpath))
            if os.path.basename(abspath) in skip_dirs:
                continue
            if not abspath in excl_paths:
                filtered_dirs.append(dirpath)
        dirs[:] = filtered_dirs

        for filename in files:
            if not is_source_file(args, filename):
                continue
            if is_excluded_path(args, filename):
                continue
            filepath = os.path.relpath(os.path.join(root, filename), abs_root)
            if not filepath in discoverd_files:
                src_report = {}
                src_report['name'] = filepath
                coverage = []
                with open(filepath) as fobj:
                    for line in fobj:
                        coverage.append(None)
                    fobj.seek(0)
                    src_report['source'] = fobj.read()
                src_report['coverage'] = coverage
                report['source_files'].append(src_report)
    report['git'] = gitrepo.gitrepo('.')
    return report
