#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pymongo
from bson import ObjectId
import file_hadndling as fh


def remove_one(collection, object_id):
    collection.delete_one({'_id': ObjectId(object_id)})


def find_all_documents(collection):
    return collection.find({})


def connect_database(database):
    secret = fh.get_secret()
    client = pymongo.MongoClient('mongodb://localhost:27017/',
                                 username='pymongo',
                                 password=secret,
                                 authSource='hashes',
                                 authMechanism='SCRAM-SHA-1')

    return client[database]
