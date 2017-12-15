#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
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
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.secret'))
    return load_document(path)[0].strip()


def insert_one(collection, mail_address_string, leak_name):
    try:
        inserted_id = collection.insert_one({'mail': mail_address_string,
                                             'leak': [leak_name]}).inserted_id
        print u'[I] Added {} with id {}'.format(mail_address_string.decode('utf-8'), inserted_id)
    except pymongo.errors.DuplicateKeyError as e:
        find_one_and_update(collection, mail_address_string, leak_name)


def find_one_and_update(collection, mail_address_string, leak_name):
    result = collection.find_one_and_update({'mail': mail_address_string},
                                            {'$addToSet': {'leak': leak_name}})
    print u'[I] Updated {} with id {}'.format(result['mail'], result['_id'])


def main():
    db = connect_database()
    collection_source = db.mail_address2
    collection_target = db.mail_address
    documents = collection_source.find()
    mail_addresses = []

    try:
        for document in documents:
            if len(document['leak']) > 1:
                for leak in document['leak']:
                    insert_one(collection_target, document['mail'], leak)
            else:
                insert_one(collection_target, document['mail'], document['leak'][0])

            mail_addresses.append(document['mail'])
    except pymongo.errors.CursorNotFound as e:
        print mail_addresses
        with open('out.txt', 'wb') as f:
            f.writelines(mail_addresses)


if __name__ == '__main__':
    main()
