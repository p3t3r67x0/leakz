#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys


def save_document(filename, document):
    with open(filename, 'wb') as f:
        f.write(document.encode('utf-8'))


def load_document(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def remove_escaped(text):
    r = re.compile(r'\&\#(\d+);')

    for m in r.findall(text):
        c = int(m)

        try:
            text = text.replace('&#{};'.format(c), unichr(c))
            print u'[I] Replaced {} with {}'.format('&#{};'.format(c), unichr(c)).encode('utf-8')
        except ValueError as e:
            pass

    return text


def match_ip_address(document):
    return re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', document)


def match_mail_address(document):
    return re.search(r'\b[\w.+-]+?@[\w]+[.]+[-_.\w]+\b', document)


def main():
    if len(sys.argv) < 3:
        sys.exit(1)

    document_lines = load_document(sys.argv[1])
    password_list = []

    for document in document_lines:
        document = document.decode('utf-8').strip('\n').strip('\r')
        document = remove_escaped(document)

        if not match_ip_address(document) and not match_mail_address(document):
            password_list.append(document)

    save_document(sys.argv[2], '\n'.join(password_list))


if __name__ == '__main__':
    main()
