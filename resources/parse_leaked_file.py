#!/usr/bin/env python
# -*- coding:utf-8 *-*


import re
import sys
import argparse


def load_document(filename):
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def extract_youporn_password(documents, args):
    password_list = set([])

    for document in documents:
        if document.startswith('password'):
            try:
                password_list.add(document.strip('\n').strip('\r').split(args.delimiter)[int(args.index)])
            except IndexError as e:
                pass

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
    documents = load_document(args.file)
    password_list = extract_youporn_password(documents, args)
    
    with open('passwords.txt', 'wb') as f:
        for password in password_list:
            f.write('{}\n'.format(password))

        f.close()

    '''
    for document in documents:
        if not document.startswith('http'):
            try:
                print document.strip('\n').strip('\r').split(args.delimiter)[int(args.index)]
            except IndexError as e:
                pass
    '''


if __name__ == '__main__':
    main()
