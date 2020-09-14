#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import bcrypt
import pymongo

from pymongo.errors import WriteError
from pymongo.errors import BulkWriteError
from pymongo.errors import DuplicateKeyError

import utils.file_handling as fh


def connect_database(database, port):
    secret = fh.get_secret()
    client = pymongo.MongoClient('mongodb://localhost:{}/'.format(port),
        username='pymongo', password=secret, authSource=database, authMechanism='SCRAM-SHA-1')

    return client[database]


def insert_one(collection, password_string, hash_string):
    try:
        inserted_id = collection.insert_one({'password': password_string, 'hash': hash_string}).inserted_id
        print('[I] Added {} with id: {}'.format(hash_string, inserted_id))
    except (DuplicateKeyError, WriteError) as e:
        print('[E] {}'.format(e))


def create_bcrypt_hash(collection):
    passwd = b"hello"

    for i in range(7998152934):
        salt = bcrypt.gensalt(rounds=12, prefix=b'2b')
        hashed_pwd = bcrypt.hashpw(passwd, salt)
        insert_one(collection, passwd, hashed_pwd)


def main():
    db = connect_database('intel', '27017')
    collection = db['bcrypt']

    try:
        collection.create_index("hash", unique=True)
    except pymongo.errors.OperationFailure as e:
        print(e)
        sys.exit(1)

    create_bcrypt_hash(collection)


if __name__ == '__main__':
    main()
