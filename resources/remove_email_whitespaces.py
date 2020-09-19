#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import pymongo

from pymongo.errors import DuplicateKeyError

import utils.database_helper as dbh
import utils.password_handling as ph
import utils.file_handling as fh


def main():
    config = json.loads(fh.get_config())
    db = dbh.connect_mongodb(config['mongodb_db'], config['mongodb_port'])
    collection = db['mails']
    documents = dbh.find_all_documents(collection)

    for document in documents:
        post = {'mail': ph.remove_whitespace(document['mail'])}
        dbh.update_one(collection, document['_id'], post)


if __name__ == '__main__':
    main()
