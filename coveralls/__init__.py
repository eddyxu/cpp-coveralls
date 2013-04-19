__author__ = 'Lei Xu <eddyxu@gmail.com>'
__version__ = '0.0.1'

__classifiers__ = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries']

__copyright__ = '2013, %s ' % __author__
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


def run():
    """Run cpp coverage."""
    import os
    import argparse
    from coveralls import coverage, report

    parser = argparse.ArgumentParser('coveralls')
    parser.add_argument('--gcov', metavar='FILE', default='gcov',
                        help='Sets the location of gcov')
    parser.add_argument('-r', '--root', metavar='DIR', default='.',
                        help='Sets the root directory')
    parser.add_argument('-e', '--exclude', metavar='DIR|FILE', action='append',
                        help='Exclude file or directory.')
    parser.add_argument('--coveralls-yaml', '-y', default='.coveralls.yml',
                        help='coveralls yaml file name')
    args = parser.parse_args()

    try:
        import yaml
    except ImportError:
        yaml = None

    yml = {}
    try:
        with open(args.coveralls_yaml, 'r') as fp:
            if yaml is None:
                raise SystemExit(
                    'PyYAML is required for parsing configuration')
            yml = yaml.load(fp)
    except IOError:
        pass
    yml = yml or {}

    args.service_name = yml.get('service_name', 'travis-ci')
    args.service_job_id = os.environ.get('TRAVIS_JOB_ID', '')

    coverage.run_gcov(args)
    cov_report = coverage.collect(args)
    report.post_report(cov_report)
