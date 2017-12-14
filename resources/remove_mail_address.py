#!/usr/bin/env python

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
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.secret'))
    return load_document(path)[0].strip()


def remove_one(collection, post):
    db.collection.delete_one({'x': 1})


def update_one(collection, document_id, post):
    try:
        collection.update_one({'_id': document_id}, {"$set": post}, upsert=False)
        print post
    except pymongo.errors.DuplicateKeyError as e:
        print u'{}'.format(e)


def find_all_documents(collection):
    return collection.find({})


def main():
    db = connect_database()
    collection = db.mail_address
    documents = find_all_documents(collection)

    for document in documents:
        if document['mail'].endswith('gmail.com777'):
            document_id = document['_id']
            mail_address = document['mail'].replace('gmail.com777', 'gmail.com')

            post = { 'mail': mail_address }
            update_one(collection, document_id, post)
            print mail_address


if __name__ == '__main__':
    main()
