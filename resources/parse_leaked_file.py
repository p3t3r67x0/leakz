#!/usr/bin/env python
# -*- coding:utf-8 *-*


import re
import sys


def load_document(filename):
    print filename
    with open(filename, 'r') as f:
        return f.readlines()


def main():
    if len(sys.argv) > 3:
        docuements = load_document(sys.argv[1])

        for docuement in docuements:
            if not docuement.startswith('http'):
                try:
                    print docuement.strip('\n').strip('\r').split(sys.argv[3])[int(sys.argv[2])]
                except IndexError as e:
                    pass


if __name__ == '__main__':
    main()
