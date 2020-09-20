#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo

from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator

from bson import ObjectId


def connect_couchdb(uri, username, password, database):
    cluster = Cluster(uri, ClusterOptions(
        PasswordAuthenticator(username, password)))
    bucket = cluster.bucket(database)

    return cluster, bucket


def delete_one(collection, document_id, context):
    collection.delete_one({'_id': ObjectId(document_id)})


def update_one(collection, document_id, post):
    collection.update_one({'_id': document_id}, {"$set": post}, upsert=True)


def find_documents(collection, skip, limit):
    return collection.find({}).skip(skip).limit(limit)


def find_conditional_documents(collection, condition):
    return collection.find(condition).sort([('$natural', 1)])


def find_all_documents(collection):
    return collection.find({}).sort([('$natural', -1)]).batch_size(30)


def connect_mongodb(database, port, secret):
    client = pymongo.MongoClient('mongodb://localhost:{}/'.format(port),
                                 username='pymongo',
                                 password=secret,
                                 authSource=database,
                                 authMechanism='SCRAM-SHA-1')

    return client[database]
