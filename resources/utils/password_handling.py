#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import hashlib


def test_md5(password):
    return re.match(r'(\b[a-fA-F\d]{32}\b)', password)


def hash_password(password):
    hash_md5 = hashlib.md5(password).hexdigest()
    hash_sha1 = hashlib.sha1(password).hexdigest()
    hash_sha224 = hashlib.sha224(password).hexdigest()
    hash_sha256 = hashlib.sha256(password).hexdigest()
    hash_sha384 = hashlib.sha384(password).hexdigest()
    hash_sha512 = hashlib.sha512(password).hexdigest()
    return {'md5': hash_md5,
            'sha1': hash_sha1,
            'sha224': hash_sha224,
            'sha256': hash_sha256,
            'sha384': hash_sha384,
            'sha512': hash_sha512}


def remove_whitespace(document):
    return document.strip().replace(' ', '')
