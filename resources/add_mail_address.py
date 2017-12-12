#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys
import pymongo


def connect_database():
    secret = get_secret()
    client = pymongo.MongoClient('mongodb://localhost:27017/',
             username='pymongo',
             password=secret,
             authSource='hashes',
             authMechanism='SCRAM-SHA-1')

    return client.hashes


def get_secret():
    return load_document('../.secret')[0].strip()


def load_document(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def handle_unicode(mail_address):
    try:
        mail_address = mail_address.encode('utf-8')
    except UnicodeDecodeError as e:
        print u'{}'.format(e)

    return mail_address


def insert_one(collection, mail_address_string, leak_name):
    try:
        inserted_id = collection.insert_one({'mail': mail_address_string,
                                             'leak': [leak_name]}).inserted_id
        print u'[I] Added {} with id {}'.format(mail_address_string.decode('utf-8'), inserted_id)
    except pymongo.errors.DuplicateKeyError as e:
        find_one_and_update(collection, mail_address_string, leak_name)


def find_one_and_update(collection, mail_address_string, leak_name):
    result = collection.find_one_and_update({'mail': mail_address_string, },
                                            {'$addToSet': {'leak': leak_name}})

    print u'[I] Updated {} with id {}'.format(result['mail'], result['_id'])


def extract_mail_address(document):
    return re.findall(r'\b[\w.+-]+?@[\w]+[.]+[-_.\w]+\b', document)


def main():
    if len(sys.argv) > 2:
        db = connect_database()
        collection = db.mail_address

        try:
            collection.create_index('mail', unique=True)
        except pymongo.errors.OperationFailure as e:
            print e
            sys.exit(1)

        document = ' '.join(load_document(sys.argv[1]))
        mail_address_list = extract_mail_address(document)
        leak_name = sys.argv[2]

        for mail_address in mail_address_list:
            mail_address = handle_unicode(mail_address.strip('\n').strip('\r').lower())
            insert_one(collection, mail_address, leak_name)


if __name__ == '__main__':
    main()
