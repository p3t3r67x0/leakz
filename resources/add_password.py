#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import pymongo
import argparse

import utils.database_helper as dbh
import utils.password_handling as ph
import utils.file_hadndling as fh
import utils.unicode_helper as uh
import utils.mail_handling as mh


reload(sys)
sys.setdefaultencoding('utf8')


def insert_one(collection, password_string, hash_string):
    try:
        inserted_id = collection.insert_one(
            {'password': password_string, 'hash': hash_string}).inserted_id
        print u'[I] Added {} with id: {}'.format(password_string, inserted_id)
    except (pymongo.errors.DuplicateKeyError, pymongo.errors.WriteError) as e:
        print u'[E] {}'.format(e)


def main():
    parser = argparse.ArgumentParser(
        description='Add passwords from file to your mongodb instance')
    parser.add_argument('-f, --file', metavar='F', required=True, dest='file',
                        help='file with absolute or relative path')

    db = dbh.connect_database('hashes')
    collection = db.password

    try:
        collection.create_index("password", unique=True)
        collection.create_index("hash.md5", unique=True)
        collection.create_index("hash.sha1", unique=True)
        collection.create_index("hash.sha224", unique=True)
        collection.create_index("hash.sha256", unique=True)
        collection.create_index("hash.sha384", unique=True)
        collection.create_index("hash.sha512", unique=True)
    except pymongo.errors.OperationFailure as e:
        print e
        sys.exit(1)

    args = parser.parse_args()
    documents = fh.load_document(args.file)

    for document in documents:
        password = document.strip()

        if password and not mh.extract_mail_address(password):
            password_string = uh.handle_unicode(password)

            if len(password_string) > 3 and len(password_string) < 24:
                hash_string = ph.hash_password(password)
                insert_one(collection, password_string, hash_string)


if __name__ == '__main__':
    main()
