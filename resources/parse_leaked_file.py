#!/usr/bin/env python
# -*- coding:utf-8 *-*


import re
import sys
import argparse


def load_document(filename):
    with open(filename, 'r') as f:
        return f.readlines()


def main():
    parser = argparse.ArgumentParser(
        description='parse leaked file to extract passwords')
    parser.add_argument('-f, --file', metavar='F', required=True, dest='file',
                        help='file with absolute or relative path')
    parser.add_argument('-i, --index', metavar='N', required=True, dest='index',
                        help='an integer will be used as index for splitting')
    parser.add_argument('-d, --delimiter', metavar='D', required=True, dest='delimiter',
                        help='a delimiter which will be used for splitting password from mail address. This will be used in every line.')

    args = parser.parse_args()
    docuements = load_document(args.file)

    for docuement in docuements:
        if not docuement.startswith('http'):
            try:
                print docuement.strip('\n').strip('\r').split(args.delimiter)[int(args.index)]
            except IndexError as e:
                pass


if __name__ == '__main__':
    main()
