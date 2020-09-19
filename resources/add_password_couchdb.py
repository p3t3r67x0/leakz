#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import sys
import json
import unicodedata

import utils.file_handling as fh
import utils.mail_handling as mh
import utils.password_handling as ph
import utils.database_helper as dbh

from couchbase.exceptions import DocumentExistsException


def filter_unicode(s):
    return ''.join(c for c in s if not unicodedata.category(c).startswith('C'))


def insert_hash(couchdb, document):
    try:
        couchdb.insert(document['sha1'], document)
        print(document)
    except DocumentExistsException as e:
        print(e)


def make_document(password):
    password_striped = re.sub(r'^(\$HEX\[.*])', '', password.strip())
    password_string = re.sub(
        r'[^\x00-\x7F]+|[\s\t ]+', '', filter_unicode(password_striped))
    result = None

    if not mh.extract_mail_address(password_string):
        if len(password_string) > 3 and len(password_string) < 32:
            result = ph.hash_password(password_string)
            result['password'] = password_string
            result['type'] = 'password'

    return result


def main():
    config = json.loads(fh.get_config())

    couchdb = dbh.connect_couchdb(
        config['COUCH_URI'], config['COUCH_USERNAME'],
        config['COUCH_PASSWORD'], config['COUCH_DATABASE'])

    documents = fh.load_document(sys.argv[1])

    for document in documents:
        doc = make_document(document)

        if doc is not None:
            insert_hash(couchdb[1], doc)


if __name__ == '__main__':
    main()
