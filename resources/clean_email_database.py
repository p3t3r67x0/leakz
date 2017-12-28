#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re

import database_helper as dbh
import mail_handling as mh


def main():
    db = dbh.connect_database('hashes')
    collection = db.mail_address
    documents = mh.find_all_documents(collection)

    for document in documents:
        if not mh.is_valid_mail(document['mail']):
            regex_match = dbh.remove_one(collection, document['_id'])

            if regex_match:
                print u'[I] removed entry {} with id {}'.format(document['mail'], document['_id'])


if __name__ == '__main__':
    main()
