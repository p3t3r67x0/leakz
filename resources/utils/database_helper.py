#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pymongo
import file_handling as fh


def delete_one(collection, document_id):
    result = collection.delete_one({'_id': document_id})
    print result.raw_result


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
