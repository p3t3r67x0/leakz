#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import hashlib
import json

from unicodedata import category

from cassandra.cqlengine.models import Model
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine import columns, connection, ValidationError

import resources.utils.hash_password as hp
import resources.utils.file_handling as fh


config = json.loads(fh.get_config())
connection.setup([config['CASSANDRA_NODES']], 'leakz', retry_connect=True)


class LeakzModel(Model):
    passphrase = columns.Text(required=True, primary_key=True)
    sha512 = columns.Text(required=True, index=True)
    sha384 = columns.Text(required=True, index=True)
    sha256 = columns.Text(required=True, index=True)
    sha224 = columns.Text(required=True, index=True)
    sha1 = columns.Text(required=True, index=True)
    md5 = columns.Text(required=True, index=True)
    ntlm = columns.Text(required=True, index=True)


sync_table(LeakzModel)


SUBS = {
    'a': '4@',
    'b': '8',
    'c': '[(',
    'd': '',
    'e': '3',
    'f': '',
    'g': '96',
    'h': '#',
    'i': '1!',
    'j': '',
    'k': '',
    'l': '1',
    'm': '',
    'n': '',
    'o': '0',
    'p': '',
    'q': '',
    'r': '',
    's': '$5',
    't': '7+',
    'u': '',
    'v': '',
    'w': '',
    'x': '',
    'y': '',
    'z': ''
}


def filter_unicode(s):
    return ''.join(c for c in s if not category(c).startswith('C'))


def leetspeak(words):
    def iter_word(word):
        if word:
            ch = word[0]

            for rest in iter_word(word[1:]):
                yield ch + rest

            for ch in SUBS.get(ch.lower(), []):
                for rest in iter_word(word[1:]):
                    yield ch + rest
        else:
            yield ''

    for word in words:
        for tmp in iter_word(word):
            yield tmp


def commit_document(p):
    d = hp.hash_password(p)

    try:
        t = LeakzModel.create(
            passphrase=p, md5=d['md5'], ntlm=d['ntlm'],
            sha1=d['sha1'], sha224=d['sha224'], sha256=d['sha256'],
            sha384=d['sha384'], sha512=d['sha512'])

        return t
    except ValidationError:
        return


def handle_document(document):
    pattern1 = r'^(\$HEX\[(.*)\]?)'
    pattern2 = r'[\s\t ]+'

    pws = re.sub(pattern1, '', document.strip())
    pw = re.sub(pattern2, '', filter_unicode(pws))
    p = ''.join(leetspeak(pw))

    if len(p) > 2 and len(p) < 20:
        commit_document(p)

    if len(pw) > 2 and len(pw) < 20:
        return commit_document(pw)


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
