#! /usr/bin/env python

import sys
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


def load_document(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def update_one(collection, document_id, post):
    try:
        collection.update_one({'_id': document_id}, {"$set": post}, upsert=False)
    except pymongo.errors.DuplicateKeyError as e:
        pass


def simple_leetspeak(text):
    return text.replace('a', '4').replace('A', '4').replace('b', '8').replace('B', '8').replace('e', '3').replace('E', '3').replace('g', '6').replace('G', '6').replace('i', '1').replace('I', '1').replace('o', '0').replace('O', '0').replace('s', '5').replace('S', '5').replace('t', '7').replace('T', '7')


def find_all_documents(collection):
    return collection.find({})


def main():
    db = connect_database()
    collection = db.password
    documents = find_all_documents(collection)

    for document in documents:
        document_id = document['_id']
        post = { 'password': simple_leetspeak(document['password']) }
        update_one(collection, document_id, post)


if __name__ == '__main__':
    main()
