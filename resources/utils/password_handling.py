#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import hashlib


def test_md5(password):
    return re.match(r'(\b[a-fA-F\d]{32}\b)', password)


def extract_pastebin_password(password):
    match = re.match(r'(\b[\w.+-]+?@[\w]+[.-]+[-_.\w]+\b)([ :]+)(.*)', password)

    if match:
        return match.group(3)
    else:
        return ''


def hash_password(password):
    password_string = password.encode('utf-8')

    hash_md5 = hashlib.md5(password_string).hexdigest()
    hash_sha1 = hashlib.sha1(password_string).hexdigest()
    hash_sha224 = hashlib.sha224(password_string).hexdigest()
    hash_sha256 = hashlib.sha256(password_string).hexdigest()
    hash_sha384 = hashlib.sha384(password_string).hexdigest()
    hash_sha512 = hashlib.sha512(password_string).hexdigest()
    return {'md5': hash_md5,
            'sha1': hash_sha1,
            'sha224': hash_sha224,
            'sha256': hash_sha256,
            'sha384': hash_sha384,
            'sha512': hash_sha512}


def remove_whitespace(document):
    return document.strip().replace(' ', '')
