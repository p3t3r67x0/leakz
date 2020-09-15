#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import sys
import json
import argparse

from pymongo.errors import WriteError
from pymongo.errors import BulkWriteError
from pymongo.errors import DuplicateKeyError
from pymongo.errors import OperationFailure

import utils.database_helper as dbh
import utils.password_handling as ph
import utils.file_handling as fh
import utils.mail_handling as mh


def insert_one(collection, password_string, hash_string):
    try:
        inserted_id = collection.insert_one(
            {'password': password_string, 'hash': hash_string}).inserted_id
        print('[I] Added {} with id: {}'.format(password_string, inserted_id))
    except (DuplicateKeyError, WriteError) as e:
        print('[E] {}'.format(e))


def insert_many(collection, data):
    try:
        collection.insert_many(data)
    except TypeError:
        pass
    except BulkWriteError:
        pass


def make_docs(docs):
    result = []

    for password in docs:
        password = re.sub(r'\s', '', password.strip())

        if not ph.test_md5(password) and not mh.extract_mail_address(password):
            if len(password) > 3 and len(password) < 32:
                result.append({
                    'password': password,
                    'hash': ph.hash_password(password)
                })

    return result


def get_progress(count):
    line = []

    for i in range(0, count, 2):
        line.append('#')

    return ''.join(line)


def print_progress(total, length, max_value=100):
    percentage = int(1 + (total / length * max_value))

    if percentage > max_value:
        percentage = max_value

    percentage_string = '{}%'.format(percentage)
    sys.stdout.write('\r{0:>68n}/{1:n}'.format(total, length))
    sys.stdout.flush()
    sys.stdout.write('\r{:>57}'.format(']'))
    sys.stdout.flush()
    sys.stdout.write('\r{:<5}[{}'.format(
        percentage_string, get_progress(percentage)))
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(
        description='Add passwords from file to your mongodb instance')
    parser.add_argument('-f, --file', metavar='F', required=True, dest='file',
                        help='file with absolute or relative path')
    parser.add_argument('-c, --create', action='store_true', dest='create')

    args = parser.parse_args()
    config = json.loads(fh.get_config())
    documents = fh.load_document(args.file)

    db = dbh.connect_database(
        config['MONGO_DB'], config['MONGO_PORT'], config['MONGO_PASSWORD'])
    collection = db['passwords']

    if args.create:
        try:
            collection.create_index("password", unique=True)
            collection.create_index("hash.md5", unique=True)
            collection.create_index("hash.sha1", unique=True)
            collection.create_index("hash.sha224", unique=True)
            collection.create_index("hash.sha256", unique=True)
            collection.create_index("hash.sha384", unique=True)
            collection.create_index("hash.sha512", unique=True)
        except OperationFailure as e:
            print('{}'.format(e))
            sys.exit(1)

    total = 0
    length = len(documents)

    for i in range(0, length, 2048):
        docs = make_docs(documents[i:i + 2048])
        insert_many(collection, docs)
        total += len(docs)
        print_progress(total, length)

    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
