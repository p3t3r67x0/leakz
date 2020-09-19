#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import json

import utils.database_helper as dbh
import utils.file_handling as fh


def match_ip_address(document):
    return re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', document)


def match_mail_address(document):
    return re.match(r'\b[\w.+-]+?[@]+[-_\w]+[.]+[-_.\w]+\b', document)


def match_full_url(document):
    return re.match(r'[\w]*?[://]+[-_\w\d]+[.]+[-_\.\w]+', document)


def main():
    config = json.loads(fh.get_config())
    db = dbh.connect_mongodb(
        config['MONGO_DB'], config['MONGO_PORT'], config['MONGO_PASSWORD'])
    amount = db['passwords'].count()
    step = 50000

    for index in range(0, amount, step):
        documents = dbh.find_documents(db['passwords'], index, (index + step))

        for document in documents:
            password = document['password']

            if match_ip_address(password):
                dbh.delete_one(db.passwords, document['_id'], password)
            elif match_mail_address(password):
                dbh.delete_one(db.passwords, document['_id'], password)
            elif match_full_url(password):
                dbh.delete_one(db.passwords, document['_id'], password)


if __name__ == '__main__':
    main()
