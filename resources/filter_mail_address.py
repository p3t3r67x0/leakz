#!/usr/bin/env python

import re
import sys


def load_document(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def match_ip_address(document):
    return re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', document)


def match_mail_address(document):
    return re.match(r'\b[\w.+-]+?@[\w]+[.]+[-_.\w]+\b', document)


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    document_lines = load_document(sys.argv[1])
    password_list = []

    for document in document_lines:
        document = document.strip('\n').strip('\r')

        if not match_mail_address and not match_mail_address:
            password_list.append(document)


    print password_list


if __name__ == '__main__':
    main()
