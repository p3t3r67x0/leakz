#!/usr/bin/env python

import re
import sys
import pymongo

def connect_database():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    return client.hashes


def delete_one(collection, document_id):
    result = collection.delete_one({'_id': document_id})
    print result.raw_result


def match_ip_address(document):
    return re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', document)


def match_mail_address(document):
    return re.search(r'\b[\w.+-]+?@[\w]+[.]+[-_.\w]+\b', document)


def find_all_documents(collection):
    return collection.find({})


def main():
    db = connect_database()
    collection = db.password
    documents = find_all_documents(collection)

    for document in documents:
        password = document['password']

        if match_ip_address(password) or match_mail_address(password):
            delete_one(collection, document['_id'])


if __name__ == '__main__':
    main()
