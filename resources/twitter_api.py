#!/usr/bin/env python3

import sys
import json
import pymongo
import twitter
import requests
import re

from urllib.parse import urlparse

from pymongo.errors import WriteError
from pymongo.errors import BulkWriteError
from pymongo.errors import DuplicateKeyError
from pymongo.errors import OperationFailure

import utils.database_helper as dbh
import utils.password_handling as ph
import utils.unicode_helper as uh
import utils.file_handling as fh
import utils.mail_handling as mh


def connect_twitter(config):
    return twitter.Api(consumer_key = config['consumer_key'],
                      consumer_secret = config['consumer_secret'],
                      access_token_key = config['access_token_key'],
                      access_token_secret = config['access_token_secret'])


def insert_password(col_password, password_string, hash_string):
    try:
        inserted_id = col_password.insert_one({'password': password_string, 'hash': hash_string}).inserted_id
        print('[I] Added {} with id: {}'.format(password_string, inserted_id))
    except (DuplicateKeyError, WriteError) as e:
        print('[E] {}'.format(e))


def insert_mail(col_mail, mail_address, leak_name):
    try:
        inserted_id = col_mail.insert_one({'mail': mail_address,
                                             'leak': [leak_name]}).inserted_id
        print('[I] Added {} with id {}'.format(mail_address.decode('utf-8'), inserted_id))
    except DuplicateKeyError as e:
        update_mail(col_mail, mail_address, leak_name)


def update_mail(col_mail, mail_address, leak_name):
    result = col_mail.find_one_and_update({'mail': mail_address, },
                                            {'$addToSet': {'leak': leak_name}})

    print('[I] Updated {} with id {}'.format(result['mail'], result['_id']))


def get_user_timeline(api, username):
    return api.GetUserTimeline(screen_name=username)


def iterate_items(statuses):
    file_content = []

    for status in statuses:
        pattern = r'(https?[\/\/\:]+[\w]+[.]+[\w\/]*)'
        m = re.search(pattern, status.text)
        req = requests.get(m.group(0))

        if req.status_code == 200:
            file_content.append(req.text)

    return file_content


def main():
    config = json.loads(fh.get_config())
    db = dbh.connect_mongodb(config['mongodb_db'], config['mongodb_port'])
    col_password = db['passwords']
    col_mail = db['mails']

    try:
        col_mail.create_index('mail', unique=True)
        col_password.create_index("password", unique=True)
        col_password.create_index("hash.md5", unique=True)
        col_password.create_index("hash.sha1", unique=True)
        col_password.create_index("hash.sha224", unique=True)
        col_password.create_index("hash.sha256", unique=True)
        col_password.create_index("hash.sha384", unique=True)
        col_password.create_index("hash.sha512", unique=True)
    except OperationFailure as e:
        print('{}'.format(e))
        sys.exit(1)

    api = connect_twitter(config)
    items = get_user_timeline(api, 'checkmydump')
    lines = iterate_items(items)

    for line in lines:
        for string in line.split('\r\n'):
            password = ph.extract_pastebin_password(re.split(r',|>>|::| |\|', string)[0])

            try:
                password = password.split(':')[0]
            except KeyError as e:
                pass

            if not mh.extract_mail_address(password):
                password_string = uh.handle_unicode(password)

                if len(password_string) > 3 and len(password_string) < 32 and not ph.test_md5(password_string):
                    insert_password(col_password, password_string, ph.hash_password(password_string))

    for mail_address in mh.extract_mail_address(''.join(lines)):
        mail_address = uh.handle_unicode(mail_address.strip().lower())
        insert_mail(col_mail, mail_address, 'pastebin.com')


if __name__ == '__main__':
    main()
