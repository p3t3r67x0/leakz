#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys
import json
import pymongo

import utils.database_helper as dbh
import utils.file_handling as fh


def match_ip_address(document):
    return re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', document)


def match_mail_address(document):
    return re.match(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', document)


def main():
    config = json.loads(fh.get_config())
    db = dbh.connect_database(config['db_name'], config['db_port_passwords'])
    documents = dbh.find_all_documents(db.password)

    for document in documents:
        password = document['password']

        if match_ip_address(password) or match_mail_address(password):
            dbh.delete_one(db.password, document['_id'])


if __name__ == '__main__':
    main()
