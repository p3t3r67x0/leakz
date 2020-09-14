#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import json
import crypt
import pymongo

import utils.database_helper as dbh
import utils.file_handling as fh


def insert_one(collection, password, hashes):
    try:
        inserted_id = collection.insert_one({'password': password, 'hash': hashes}).inserted_id
        print('[I] Added {} with id {}'.format(password, inserted_id))
    except pymongo.errors.DuplicateKeyError as e:
        print(e)


def generate_shadow_hash(collection, password, salt):
    print(dir(crypt.crypt))

    hashes = {
        'md5': crypt.crypt(password, '$1$' + salt),
        'sha256': crypt.crypt(password, '$5$' + salt),
        'sha512': crypt.crypt(password, '$6$' + salt)
    }

    # insert_one(collection, password, hashes)


def load_passwords(filename):
    with open(filename, 'r') as f:
        passwords = f.readlines()

    return passwords


def main():
    config = json.loads(fh.get_config())
    db = dbh.connect_database(config['MONGO_DB'], config['MONGO_PORT'], config['MONGO_PASSWORD'])
    collection = db['shadow']

    try:
        collection.create_index("hash.md5", unique=True)
        collection.create_index("hash.sha256", unique=True)
        collection.create_index("hash.sha512", unique=True)
    except pymongo.errors.OperationFailure as e:
        print(e)
        sys.exit(1)

    passwords = load_passwords(sys.argv[1])

    for password in passwords:
        # $1$GQ7Z9vnb$8Bf1DbyfMHO13ubVZaZuv/
        generate_shadow_hash(collection, password.strip(), 'GQ7Z9vnb')


if __name__ == '__main__':
    main()
