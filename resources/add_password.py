#!/usr/bin/env python
# -*- coding:utf-8 -*-


import re
import sys
import pymongo
import hashlib

reload(sys)
sys.setdefaultencoding('utf8')


def load_passwords(filename):
    with open(filename, 'rb') as f:
        return f.readlines()


def handle_unicode(password):
    try:
        password_string = password.decode('utf-8')
    except UnicodeDecodeError as e:
        try:
            password_string = password.encode('utf-8')
        except UnicodeDecodeError as e:
            password_string = password.decode('ascii')
            print u'{}'.format(e)

    return password_string


def connect_database():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    return client.hashes


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


def insert_one(collection, password, hash_string):
    try:
        password_string = password.strip('\n').strip('\r')
        inserted_id = collection.insert_one(
            {'password': password_string, 'hash': hash_string}).inserted_id
        print u'[I] Added {} with id: {}'.format(password_string, inserted_id)
    except (pymongo.errors.DuplicateKeyError, pymongo.errors.WriteError) as e:
        print u'[E] {}'.format(e)


def extract_mail_address(document):
    return re.findall(r'\b[\w.+-]+?@[\w]+[.]+[-_.\w]+\b', document)


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    db = connect_database()
    db.password.create_index("password", unique=True)
    collection = db.password

    with open(sys.argv[1]) as f:
        while f:
            for line in f.readlines(1024):
                password = line.strip()

                if password and not extract_mail_address(password):
                    hash_string = hash_password(password)
                    password_string = handle_unicode(password)
                    insert_one(collection, password_string, hash_string)


if __name__ == '__main__':
    main()
