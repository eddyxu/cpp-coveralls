from __future__ import absolute_import
from __future__ import print_function

__author__ = 'Lei Xu <eddyxu@gmail.com>'
__version__ = '0.4.2'

__classifiers__ = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Utilities',
]

__copyright__ = '2019, %s ' % __author__
__license__ = """
    Copyright %s.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    """ % __copyright__

def parse_yaml_config(args):
    """Parse yaml config"""
    try:
        import yaml
    except ImportError:
        yaml = None

    yml = {}
    try:
        with open(args.coveralls_yaml, 'r') as fp:
            if not yaml:
                raise SystemExit('PyYAML is required for parsing configuration')
            yml = yaml.load(fp)
    except IOError:
        pass
    yml = yml or {}
    return yml

def run():
    """Run cpp coverage."""
    import json
    import os
    import sys
    import time
    from . import coverage, report

    args = coverage.create_args(sys.argv[1:])

    if args.verbose:
        print('encodings: {}'.format(args.encodings))

    yml = parse_yaml_config(args)

    if not args.repo_token:
        # try get token from yaml first
        args.repo_token = yml.get('repo_token', '')
    if not args.repo_token:
        # use environment COVERALLS_REPO_TOKEN as a fallback
        args.repo_token = os.environ.get('COVERALLS_REPO_TOKEN')

    if not args.gcov_options:
        args.gcov_options = yml.get('gcov_options', '')
    if not args.root:
        args.root = yml.get('root', '.')
    if not args.build_root:
        args.build_root = yml.get('build_root', '')

    args.exclude.extend(yml.get('exclude', []))
    args.include.extend(yml.get('include', []))
    args.exclude_lines_pattern.extend(yml.get('exclude_lines_pattern', []))

    args.service_name = os.environ.get('CI_NAME', '')
    args.service_job_id = os.environ.get('CI_BUILD_NUMBER', '')
    args.service_pull_request = os.environ.get('CI_PULL_REQUEST', 'false')

    if args.repo_token == '' and args.service_job_id == '':
        raise ValueError("\nno coveralls.io token specified and no travis job id found\n"
                         "see --help for examples on how to specify a token\n")

    if args.service_job_id == '':
        epoch = str(time.time()).split('.')[0]
        args.service_job_id = "%s-%s" % (os.environ.get('CI_BRANCH', ''), epoch)

    if not args.no_gcov:
        coverage.run_gcov(args)
    cov_report = coverage.collect(args)
    if args.verbose:
        print(cov_report)
    if args.dryrun:
        return 0
    if args.dump:
        args.dump.write(json.dumps(cov_report))
        return 0

    return report.post_report(cov_report, args)
