#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys


def load_document(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def get_secret():
    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../.secret'))
    return load_document(path)[0].strip()
