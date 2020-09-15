#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import unicodedata

import utils.file_handling as fh


def filter_non_printable(s):
    return ''.join(c for c in s if not unicodedata.category(c).startswith('C'))


def main():
    documents = fh.load_document(sys.argv[1])
    lines = []

    for line in documents:
        lines.append(re.sub(r'[\s\t ]+', '', filter_non_printable(line)))

    fh.save_document('output_{}.txt'.format(
        os.path.basename(sys.argv[1])), '\n'.join(lines))


if __name__ == '__main__':
    main()
