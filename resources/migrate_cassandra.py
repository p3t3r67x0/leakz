#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import json

from unicodedata import category

from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import ValidationError

from pymongo.errors import CursorNotFound

import utils.database_helper as dbh
import utils.hash_password as hp
import utils.file_handling as fh


connection.setup(['127.0.0.1'], 'leakz', retry_connect=True)


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


def main():
    config = json.loads(fh.get_config())

    mongodb = dbh.connect_mongodb(
        config['MONGO_DB'], config['MONGO_PORT'], config['MONGO_PASSWORD'])

    condition = {'import': {'$exists': False}}
    collection = mongodb['passwords']

    documents = dbh.find_conditional_documents(collection, condition)

    for document in documents:
        try:
            pattern1 = r'^(\$HEX\[(.*)\]?)'
            pattern2 = r'[\s\t ]+|[^\x00-\x7F]+|[\s\t ]+'

            pws = re.sub(pattern1, '', document['password'])
            pw = re.sub(pattern2, '', filter_unicode(pws))
            p = ''.join(leetspeak(pw))

            dbh.update_one(collection, document['_id'], {'import': True})

            if len(pw) > 3 and len(pw) < 20:
                print(commit_document(pw))

            if len(p) > 3 and len(p) < 20:
                print(commit_document(p))

        except CursorNotFound:
            continue


if __name__ == '__main__':
    main()
