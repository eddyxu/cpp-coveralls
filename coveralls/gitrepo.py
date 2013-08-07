import locale
import os
import subprocess


def gitrepo(self):
    """Return hash of Git data that can be used to display more information to
    users.

    Example:
        "git": {
            "head": {
                "id": "5e837ce92220be64821128a70f6093f836dd2c05",
                "author_name": "Wil Gieseler",
                "author_email": "wil@example.com",
                "committer_name": "Wil Gieseler",
                "committer_email": "wil@example.com",
                "message": "depend on simplecov >= 0.7"
            },
            "branch": "master",
            "remotes": [{
                "name": "origin",
                "url": "https://github.com/lemurheavy/coveralls-ruby.git"
            }]
        }

    From https://github.com/coagulant/coveralls-python (with MIT license).

    """

    return {
        'head': {
            'id': gitlog('%H'),
            'author_name': gitlog('%aN'),
            'author_email': gitlog('%ae'),
            'committer_name': gitlog('%cN'),
            'committer_email': gitlog('%ce'),
            'message': gitlog('%s')
        },
        'branch': os.environ.get('TRAVIS_BRANCH', git(
            'rev-parse', '--abbrev-ref', 'HEAD').strip()),
        'remotes': [{'name': line.split()[0], 'url': line.split()[1]}
                    for line in git('remote', '-v') if '(fetch)' in line]
    }


def gitlog(format):
    return git('--no-pager', 'log', '-1', '--pretty=format:%s' % format)


def git(*arguments):
    """Return output from git."""
    process = subprocess.Popen(['git'] + list(arguments),
                               stdout=subprocess.PIPE)
    return process.communicate()[0].decode('UTF-8')
