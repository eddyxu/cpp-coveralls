#!/usr/bin/python

from __future__ import absolute_import
from __future__ import print_function

import json
import sys

expectedJson="expected.json"
if sys.argv[1] == "-e":
    expectedJson = sys.argv[2]


expected=json.loads(open(expectedJson).read())
output=json.loads(open("output.json").read())

if 'source_files' not in expected:
    print ("expected.json does not contain a 'source_files' array")
    print(expected)
    exit (1)

if 'source_files' not in output:
    print ("output.json does not contain a 'source_files' array")
    print(output)
    exit (1)

expected_files={}
output_files={}

for f in expected['source_files']:
    expected_files[f['name']] = f
for f in output['source_files']:
    output_files[f['name']] = f

#
# Check for missing files
#
for f in expected_files:
    if f not in output_files:
        print ("File '%s' is missing from output.json" %f)
        exit(1)
#
# Check for rogue files
#
for f in output_files:
    if f not in expected_files:
        print ("File '%s' is reported in output.json, but was not expected!" %f)
        exit(1)

#
# Finally check each file has the expected output...
#
for f in expected_files:
    exp_file = expected_files[f]
    out_file = output_files[f]

    exp_lines=exp_file['coverage']
    out_lines=out_file['coverage']
    if len(exp_lines) != len(out_lines):
        print ("File '%s': expected %d lines, but actually has %s" %(f, len(exp_lines), len(out_lines)))
        exit(1)

    for i in range(len(out_lines)):
        if exp_lines[i] != out_lines[i]:
            print ("File '%s':%d, expected %s hits, but actually has %s" %(f, i+1, exp_lines[i], out_lines[i]))
            exit(1)



