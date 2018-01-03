#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import pymongo

from pymongo.errors import DuplicateKeyError

import utils.database_helper as dbh
import utils.password_handling as ph
import utils.file_handling as fh


def update_one(collection, document_id, post):
    try:
        collection.update_one({'_id': document_id}, {
                              "$set": post}, upsert=True)
    except DuplicateKeyError as e:
        print u'{}'.format(e)


def main():
    config = json.loads(fh.get_config())
    db = dbh.connect_database('hashes', config['db_port_mail'])
    collection = db['mails']
    documents = dbh.find_all_documents(collection)

    for document in documents:
        document_id = document['_id']

        post = {'mail': ph.remove_whitespace(document['mail'])}
        update_one(collection, document_id, post)


if __name__ == '__main__':
    main()
