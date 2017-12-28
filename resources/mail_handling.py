#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re



def find_all_documents(collection):
    return collection.find({})


def extract_mail_address(document):
    return re.findall(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', document)


def is_valid_mail(mail_address_string):
    return re.match(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', mail_address_string)
