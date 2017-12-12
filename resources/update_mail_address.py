#!/usr/bin/env python
# -*- coding:utf-8 -*-

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


def update_one(collection, document_id, post):
    try:
        collection.update_one({'_id': document_id}, {"$set": post}, upsert=False)
    except pymongo.errors.DuplicateKeyError as e:
        print u'{}'.format(e)


def find_all_documents(collection):
    return collection.find({})


def main():
    db = connect_database()
    collection = db.mail_address

    documents = find_all_documents(collection)

    for document in documents:
        document_id = document['_id']
        mail_address = document['mail'].strip('\n').strip('\r')

        post = { 'mail': mail_address }
        update_one(collection, document_id, post)


if __name__ == '__main__':
    main()
