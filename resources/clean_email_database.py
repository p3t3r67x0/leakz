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
    db = dbh.connect_database(config['db_name'], config['db_port_mails'])
    collection = db['mail_address']
    amount = db['mails'].count()
    step = 50000

    for index in xrange(0, amount, step):
        documents = dbh.find_documents(db['mails'], index, (index + step))

        for document in documents:
            if not mh.is_valid_mail(document['mail']):
                dbh.delete_one(collection, document['_id'], document['mail'])


if __name__ == '__main__':
    main()
