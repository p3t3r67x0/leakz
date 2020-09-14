#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys


def load_document(filename):
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except IOError as e:
        print(e)
        sys.exit(1)


def save_document(filename, document):
    with open(filename, 'w') as f:
        f.write(document)


def get_config():
    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../../config.json'))
    return ''.join(load_document(path))
