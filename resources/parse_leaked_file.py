#!/usr/bin/env python
# -*- coding:utf-8 *-*

import os
import re
import sys
import argparse


import file_hadndling as fh


def split_line(document, args):
    try:
        return document.strip().split(args.delimiter)[int(args.index)]
    except IndexError as e:
        return


def extract_password(documents, args):
    password_list = set([])

    for document in documents:
        password_list.add(split_line(document, args))

    return password_list


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
    documents = fh.load_document(args.file)
    password_list = extract_password(documents, args)

    with open('passwords.txt', 'wb') as f:
        for password in password_list:
            f.write('{}\n'.format(password))

        f.close()


if __name__ == '__main__':
    main()
