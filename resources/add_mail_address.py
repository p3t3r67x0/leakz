#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys
import pymongo

import utils.database_helper as dbh
import utils.unicode_helper as uh
import utils.file_hadndling as fh
import utils.mail_handling as mh


def insert_one(collection, mail_address_string, leak_name):
    try:
        inserted_id = collection.insert_one({'mail': mail_address_string,
                                             'leak': [leak_name]}).inserted_id
        print u'[I] Added {} with id {}'.format(mail_address_string.decode('utf-8'), inserted_id)
    except pymongo.errors.DuplicateKeyError as e:
        find_one_and_update(collection, mail_address_string, leak_name)


def find_one_and_update(collection, mail_address_string, leak_name):
    result = collection.find_one_and_update({'mail': mail_address_string, },
                                            {'$addToSet': {'leak': leak_name}})

    print u'[I] Updated {} with id {}'.format(result['mail'], result['_id'])


def main():
    if len(sys.argv) > 2:
        db = dbh.connect_database('hashes')
        collection = db.mail_address

        try:
            collection.create_index('mail', unique=True)
        except pymongo.errors.OperationFailure as e:
            print u'{}'.format(e)
            sys.exit(1)

        document = ' '.join(fh.load_document(sys.argv[1]))
        mail_address_list = mh.extract_mail_address(document)
        leak_name = sys.argv[2]

        for mail_address in mail_address_list:
            mail_address = uh.handle_unicode(
                mail_address.strip('\n').strip('\r').lower())
            insert_one(collection, mail_address, leak_name)


if __name__ == '__main__':
    main()
