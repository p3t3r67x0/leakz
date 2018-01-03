#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys
import pymongo
import argparse

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
    parser = argparse.ArgumentParser(
        description='Add mail addresses from file to your mongodb instance')
    parser.add_argument('-f, --file', metavar='F', required=True, dest='file',
                        help='non structured document with leaked mail addresses')
    parser.add_argument('-p, --port', metavar='P', required=True, dest='port',
                        help='define mongodb port to connect the database')
    parser.add_argument('-l, --leak', metavar='L', required=True, dest='leak',
                        help='set leaked website or organistion name here')

    args = parser.parse_args()
    db = dbh.connect_database('hashes', args.port)
    collection = db['mails']

    try:
        collection.create_index('mail', unique=True)
    except pymongo.errors.OperationFailure as e:
        print u'{}'.format(e)
        sys.exit(1)

    document = ' '.join(fh.load_document(args.file))
    mail_address_list = mh.extract_mail_address(document)

    for mail_address in mail_address_list:
        mail_address = uh.handle_unicode(mail_address.strip().lower())
        insert_one(collection, mail_address, args.leak)


if __name__ == '__main__':
    main()
