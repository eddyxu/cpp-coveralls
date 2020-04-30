from __future__ import absolute_import
from __future__ import print_function

import requests
import json
import os

ENDPOINT = os.getenv('COVERALLS_ENDPOINT', 'https://coveralls.io')

def post_report(coverage, args):
    """Post coverage report to coveralls.io."""
    api_endpoint = f'{ENDPOINT}/api/v1/jobs'
    response = requests.post(api_endpoint, files={'json_file': json.dumps(coverage)},
                             verify=(not args.skip_ssl_verify))
    try:
        result = response.json()
    except ValueError:
        result = {'error': 'Failure to submit data. '
                  'Response [%(status)s]: %(text)s' % {
                      'status': response.status_code,
                      'text': response.text}}
    print(result)
    if 'error' in result:
        return result['error']
    return 0

def finish_report(args):
    """Finish a parallel reporting: https://docs.coveralls.io/parallel-build-webhook"""
    api_endpoint = f'{ENDPOINT}/webhook?repo_token={args.repo_token}'
    data = {'payload[build_num]': args.service_number, 'payload[status]':'done'}
    response = requests.post(api_endpoint, data=data,
        verify=(not args.skip_ssl_verify))

    if response.status_code != 200:
        return response.status_code, response.reason, data
    else:
        return 0