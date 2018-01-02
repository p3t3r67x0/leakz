#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import json
import pymongo

import utils.database_helper as dbh
import utils.file_handling as fh


def insert_one(collection, mail_address_string, leak_name):
    try:
        inserted_id = collection.insert_one({'mail': mail_address_string,
                                             'leak': [leak_name]}).inserted_id
        print u'[I] Added {} with id {}'.format(mail_address_string.decode('utf-8'), inserted_id)
    except pymongo.errors.DuplicateKeyError as e:
        find_one_and_update(collection, mail_address_string, leak_name)


def find_one_and_update(collection, mail_address_string, leak_name):
    result = collection.find_one_and_update({'mail': mail_address_string},
                                            {'$addToSet': {'leak': leak_name}})
    print u'[I] Updated {} with id {}'.format(result['mail'], result['_id'])


def main():
    config = json.loads(fh.get_config())
    db = dbh.connect_database('hashes', config['db_port_mail'])
    collection_source = db.mail_address2
    collection_target = db.mail_address
    documents = dbh.find_all_documents(collection_source)
    mail_addresses = []

    try:
        for document in documents:
            if len(document['leak']) > 1:
                for leak in document['leak']:
                    insert_one(collection_target, document['mail'], leak)
            else:
                insert_one(collection_target,
                           document['mail'], document['leak'][0])

            mail_addresses.append(document['mail'])
    except pymongo.errors.CursorNotFound as e:
        print mail_addresses
        with open('out.txt', 'wb') as f:
            f.writelines(mail_addresses)


if __name__ == '__main__':
    main()
