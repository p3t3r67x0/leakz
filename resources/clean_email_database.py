#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import json

import utils.database_helper as dbh
import utils.mail_handling as mh
import utils.file_handling as fh


def main():
    config = json.loads(fh.get_config())
    db = dbh.connect_database(config['db_name'], config['db_port_mail'])
    collection = db.mail_address
    documents = dbh.find_all_documents(collection)

    for document in documents:
        if not mh.is_valid_mail(document['mail']):
            regex_match = dbh.delete_one(collection, document['_id'])

            if regex_match:
                print u'[I] removed entry {} with id {}'.format(document['mail'], document['_id'])


if __name__ == '__main__':
    main()
