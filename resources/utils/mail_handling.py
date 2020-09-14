#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re


def extract_mail_address(document):
    return re.findall(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', document)


def is_valid_mail(document):
    return re.match(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', document)
