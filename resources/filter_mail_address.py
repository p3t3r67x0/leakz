#!/usr/bin/env python

import re
import sys


def save_document(filename, document):
    with open(filename, 'wb') as f:
        f.write(document)


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
    return re.search(r'\b[\w.+-]+?@[\w]+[.]+[-_.\w]+\b', document)


def main():
    if len(sys.argv) < 3:
        sys.exit(1)

    document_lines = load_document(sys.argv[1])
    password_list = []

    for document in document_lines:
        document = document.strip('\n').strip('\r')

        if not match_ip_address(document) and not match_mail_address(document):
            password_list.append(document)

    save_document(sys.argv[2], '\n'.join(password_list))


if __name__ == '__main__':
    main()
