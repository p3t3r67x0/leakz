#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import pymongo


def connect_database():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    return client.hashes


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

    for document in documents:
        if len(document['leak']) > 1:
            for leak in document['leak']:
                insert_one(collection_target, document['mail'], leak)
        else:
            insert_one(collection_target, document['mail'], document['leak'][0])

        print '\n\n'


if __name__ == '__main__':
    main()
