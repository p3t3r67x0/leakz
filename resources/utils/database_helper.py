#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pymongo
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from . import file_handling as fh


def delete_one(collection, document_id, context):
    result = collection.delete_one({'_id': ObjectId(document_id)})

    if result.deleted_count:
        print(('[I] deleted {} from collection: {}'.format(context, collection._Collection__name)))


def update_one(collection, document_id, post):
    try:
        collection.update_one({'_id': document_id}, {
                              "$set": post}, upsert=True)
    except DuplicateKeyError as e:
        print(('{}'.format(e)))


def find_documents(collection, skip, limit):
    return collection.find({}).skip(skip).limit(limit)


def find_all_documents(collection):
    return collection.find({}).sort([('$natural', -1)]).batch_size(30)


def connect_database(database, port, secret):
    client = pymongo.MongoClient('mongodb://localhost:{}/'.format(port),
                                 username='pymongo',
                                 password=secret,
                                 authSource=database,
                                 authMechanism='SCRAM-SHA-1')

    return client[database]
