#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pymongo
from bson import ObjectId

import file_handling as fh


def delete_one(collection, document_id, password):
    result = collection.delete_one({'_id': ObjectId(document_id)})

    if result.deleted_count:
        print u'[I] deleted {} from collection: {}'.format(password, collection._Collection__name)


def find_documents(collection, skip, limit):
    return collection.find({}).skip(skip).limit(limit)


def find_all_documents(collection):
    return collection.find({})


def connect_database(database, port):
    secret = fh.get_secret()
    client = pymongo.MongoClient('mongodb://localhost:{}/'.format(port),
                                 username='pymongo',
                                 password=secret,
                                 authSource=database,
                                 authMechanism='SCRAM-SHA-1')

    return client[database]
