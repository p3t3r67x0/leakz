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


def insert_one(collection, mail_address):
    try:
        mail_address_string = mail_address.strip('\n').strip('\r').lower()
        inserted_id = collection.insert_one({ 'mail': mail_address_string }).inserted_id
        print u'[I] Added {} with id {}'.format(mail_address_string.decode('utf-8'), inserted_id)
    except pymongo.errors.DuplicateKeyError as e:
        print u'{}'.format(e)


def extract_mail_address(document):
    return re.findall(r'\b[\w.+-]+?@\w*[-\.\w+?]*\b', document)


def main():
    if len(sys.argv) > 1:
        db = connect_database()
        db.mail_address.create_index('mail', unique=True)
        collection = db.mail_address

        document = ' '.join(load_document(sys.argv[1]))
        mail_address_list = extract_mail_address(document)

        for mail_address in mail_address_list:
            mail_address = handle_unicode(mail_address.strip('\n').strip('\r'))
            insert_one(collection, mail_address)


if __name__ == '__main__':
    main()
