#!/usr/bin/env python
# -*- coding:utf-8 -*-


import re
import pymongo
from bson import ObjectId


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


def find_all_documents(collection):
	return collection.find({})


def is_valid_mail(mail_address_string):
	return re.match(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', mail_address_string)


def remove_one(collection, object_id):
    collection.delete_one({ '_id': ObjectId(object_id) })


def main():
    db = connect_database()
    collection = db.mail_address
    documents = find_all_documents(collection)

    for document in documents:
        if not is_valid_mail(document['mail']):
            regex_match = remove_one(collection, document['_id'])

            if regex_match:
                print u'[I] removed entry {} with id {}'.format(document['mail'], document['_id'])


if __name__ == '__main__':
    main()
