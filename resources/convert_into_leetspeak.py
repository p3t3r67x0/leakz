#! /usr/bin/env python

import os
import sys
import json
import pymongo
import hashlib

from pymongo.errors import WriteError
from pymongo.errors import DuplicateKeyError

import utils.database_helper as dbh
import utils.password_handling as ph
import utils.file_handling as fh


def insert_one(collection, password_string, hash_string):
    try:
        inserted_id = collection.insert_one(
            {'password': password_string.decode('utf-8'), 'hash': hash_string}).inserted_id
        print('[I] Added {} with id: {}'.format(password_string.decode('utf-8'), inserted_id))
    except (UnicodeDecodeError) as e:
        print('[E] {}'.format(e))
        sys.exit(1)
    except (DuplicateKeyError, WriteError) as e:
        print('[E] {}'.format(e))


def simple_leetspeak(text):
    pattern = {'a': '4', 'A': '4', 'b': '8', 'B': '8', 'e': '3', 'E': '3', 'g': '6',
               'G': '6', 'i': '1', 'I': '1', 'o': '0', 'O': '0', 's': '5', 'S': '5',
               't': '7', 'T': '7'}

    for key, value in pattern.items():
        text = text.replace(key, value)

    return text


def main():
    config = json.loads(fh.get_config())
    db = dbh.connect_database(config['db_name'], config['db_port_passwords'])
    collection = db['passwords']

    try:
        collection.create_index("password", unique=True)
        collection.create_index("hash.md5", unique=True)
        collection.create_index("hash.sha1", unique=True)
        collection.create_index("hash.sha224", unique=True)
        collection.create_index("hash.sha256", unique=True)
        collection.create_index("hash.sha384", unique=True)
        collection.create_index("hash.sha512", unique=True)
    except pymongo.errors.OperationFailure as e:
        print(e)
        sys.exit(1)

    documents = dbh.find_all_documents(collection)

    for document in documents:
        password = document['password'].encode('utf-8')
        leetspeak = simple_leetspeak(password)

        if leetspeak != password:
            hash_string = ph.hash_password(leetspeak)
            insert_one(collection, leetspeak, hash_string)


if __name__ == '__main__':
    main()
