# Copyright 2013 (c) Lei Xu <eddyxu@gmail.com>

import os
import subprocess
from coveralls import gitrepo


def is_source_file(filepath):
    """Returns true if it is a C++ source file
    """
    return os.path.splitext(filepath)[1] in ['.h', '.hpp', '.cpp', '.cc', '.c']


def run_gcov(args):
    for root, dirs, files in os.walk(args.root):
        for dirpath in dirs:
            if dirpath == 'test':
                dirs.remove(dirpath)
        for filepath in files:
            basename, ext = os.path.splitext(filepath)
            if ext == '.gcno':
                subprocess.call('cd %s && %s %s' % (root, args.gcov, basename),
                                shell=True)


def collect(args):
    """Collect coverage reports.
    """
    report = {}
    report['service_name'] = args.service_name
    report['service_job_id'] = args.service_job_id
    report['source_files'] = []
    for root, dirs, files in os.walk(args.root):
        for dirpath in dirs:
            if dirpath == 'test':
                dirs.remove(dirpath)
            #if os.path.join(root, dirpath) in args.exclude:
            #    dirs.remove(dirpath)
        for filepath in files:
            if is_source_file(filepath):
                src_path = os.path.relpath(os.path.join(root, filepath), '.')
                gcov_path = src_path + '.gcov'
                src_report = {}
                src_report['name'] = src_path
                with open(src_path) as fobj:
                    src_report['source'] = fobj.read()

                coverage = []
                if os.path.exists(gcov_path):
                    with open(gcov_path) as fobj:
                        for line in fobj:
                            report_fields = line.split(':')
                            cov_num = report_fields[0].strip()
                            line_num = int(report_fields[1].strip())
                            if line_num == 0:
                                continue
                            if cov_num == '-':
                                coverage.append(None)
                            elif cov_num == '#####':
                                coverage.append(0)
                            else:
                                coverage.append(int(cov_num))
                src_report['coverage'] = coverage
                report['source_files'].append(src_report)
    report['git'] = gitrepo.gitrepo('.')
    return report
