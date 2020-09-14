#!/usr/bin/env python3

import re
import sys
import csv


def match_length(string):
    hash = {
        30, 32, 40, 56, 64, 96, 128
    }

    m1 = re.match(r'^\$(p|2y|sha|1)\$.*', string)
    m2 = re.match(r'^[0-9a-fA-F]+$', string)
    m3 = re.match(r'\b[0-9a-fA-F]+:\w{2,}\b', string)
    m4 = re.match(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', string)
    m5 = re.match(r'[\w?://]+[-_\w\d]+[.]+[-_\.\w]+', string)

    if len(string) not in hash and not m1 and not m2 and not m3 and not m4 and not m5:
        return string
    else:
        return


def load_document(filename):
    with open(filename, 'r') as f:
        rows = csv.reader(f, delimiter=',')
        for row in rows:
            if match_length(row[3]):
                print(row[3])


def main():
    load_document(sys.argv[1])


if __name__ == '__main__':
    main()
