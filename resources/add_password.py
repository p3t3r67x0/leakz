#!/usr/bin/env python
# -*- coding:utf-8 -*-


import sys
import pymongo
import hashlib


def load_passwords(filename):
    with open(filename, 'rb') as f:
        return f.readlines()


def handle_unicode(password):
    try:
        password_string = password.encode('utf-8')
    except UnicodeDecodeError as e:
        print u'{}'.format(e)
        try:
            password_string = password.decode('iso-8859-1')
        except UnicodeDecodeError as e:
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
            'sha224': hash_sha224,
            'sha256': hash_sha256,
            'sha384': hash_sha384,
            'sha512': hash_sha512}


def insert_one(collection, password, hash_string):
    try:
        a = collection.insert_one({'password': password.strip('\n'), 'hash': hash_string}).inserted_id
        print a
    except pymongo.errors.DuplicateKeyError as e:
        print u'{}'.format(e)


def main():
    if len(sys.argv) > 1:
        password_list = load_passwords(sys.argv[1])
        db = connect_database()
        db.password.create_index("password", unique=True)
        collection = db.password

        for password in password_list:
            hash_string = hash_password(password)
            password_string = handle_unicode(password)
            insert_one(collection, password_string, hash_string)


if __name__ == '__main__':
    main()
