#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json

import utils.database_helper as dbh
import utils.file_handling as fh

from pymongo.errors import CursorNotFound

from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator
from couchbase.exceptions import DocumentExistsException, TimeoutException


def connect_couchdb(uri, username, password, database):
    cluster = Cluster(uri, ClusterOptions(
        PasswordAuthenticator(username, password)))
    cb = cluster.bucket(database)

    return cb


def insert_hash(couchdb, document):
    try:
        doc = document['hash']
        doc['type'] = 'password'
        doc['password'] = document['password']
        couchdb.insert(document['hash']['sha1'], doc)
        print(doc)
    except DocumentExistsException as e:
        print(e)


def main():
    config = json.loads(fh.get_config())

    couchdb = connect_couchdb(
        config['COUCH_URI'], config['COUCH_USERNAME'],
        config['COUCH_PASSWORD'], config['COUCH_DATABASE'])
    mongodb = dbh.connect_database(
        config['MONGO_DB'], config['MONGO_PORT'], config['MONGO_PASSWORD'])

    condition = {'import': {'$exists': False}}
    collection = mongodb['passwords']

    documents = dbh.find_collectional_documents(collection, condition)

    for document in documents:
        try:
            insert_hash(couchdb, document)
            dbh.update_one(collection, document['_id'], {'import': True})
        except CursorNotFound:
            pass
        except TimeoutException:
            pass


if __name__ == '__main__':
    main()
