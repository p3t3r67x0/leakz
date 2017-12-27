#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
from operator import itemgetter

import os
import re
import pymongo


def connect_database():
    secret = get_secret()
    client = pymongo.MongoClient('mongodb://localhost:27017/',
             username='pymongo',
             password=secret,
             authSource='hashes',
             authMechanism='SCRAM-SHA-1')

    return client.hashes


def get_secret():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.secret'))
    return load_document(path)[0].strip()


def main():
    db = connect_database()
    collection = db.mail_address
    stat_dict = {}

    mail_address_list = collection.find({})

    for mail_address in mail_address_list:
        mail_address = mail_address['mail']
        m = re.match(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', mail_address)

        try:
            mail_address = m.group(1).lower()

            if not mail_address in stat_dict:
                stat_dict[mail_address] = 1
            else:
                stat_dict[mail_address] = stat_dict[mail_address] + 1
        except AttributeError as e:
            pass

    sorted_list = []
    vol_amount_all = 0

    for item in sorted(stat_dict.items(), key=lambda x: x[1], reverse=True):
        vol_amount_all = item[1] + vol_amount_all
        sorted_list.append(item)

    for i in sorted_list:
        calc = round(i[1] / vol_amount_all * 100, 2)

        if calc > 0:
            print calc, i[0]


if __name__ == '__main__':
    main()
