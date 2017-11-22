#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys
import pymongo
import hashlib


def load_document(filename):
    with open(filename, 'rb') as f:
        return f.readlines()


def handle_unicode(mail_address):
    try:
        mail_address = mail_address.encode('utf-8')
    except UnicodeDecodeError as e:
        print u'{}'.format(e)

    return mail_address


def connect_database():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    return client.hashes


def insert_one(collection, mail_address_string, leak_name):
    try:
        inserted_id = collection.insert_one({ 'mail': mail_address_string,
                                             'leak': [ leak_name ] }).inserted_id
        print u'[I] Added {} with id {}'.format(mail_address_string.decode('utf-8'), inserted_id)
    except pymongo.errors.DuplicateKeyError as e:
        find_one_and_update(collection, mail_address_string, leak_name)


def find_one_and_update(collection, mail_address_string, leak_name):
    result = collection.find_one_and_update({ 'mail': mail_address_string, },
                                   { '$addToSet': { 'leak': leak_name }} )

    print u'[I] Updated {} with id {}'.format(result['mail'], result['_id'])


def extract_mail_address(document):
    return re.findall(r'\b[\w.+-]+?@\w*[-\.\w+?]*\b', document)


def main():
    if len(sys.argv) > 2:
        db = connect_database()
        db.mail_address.create_index('mail', unique=True)
        collection = db.mail_address

        document = ' '.join(load_document(sys.argv[1]))
        mail_address_list = extract_mail_address(document)
        leak_name = sys.argv[2]

        for mail_address in mail_address_list:
            mail_address = handle_unicode(mail_address.strip('\n').strip('\r').lower())
            insert_one(collection, mail_address, leak_name)


if __name__ == '__main__':
    main()
