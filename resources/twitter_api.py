#!/usr/bin/env python

import sys
import json
import pymongo
import twitter
import requests
import re

import utils.database_helper as dbh
import utils.unicode_helper as uh
import utils.file_handling as fh
import utils.mail_handling as mh


def connect_twitter(config):
    return twitter.Api(consumer_key = config['consumer_key'],
                      consumer_secret = config['consumer_secret'],
                      access_token_key = config['access_token_key'],
                      access_token_secret = config['access_token_secret'])


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
    db = dbh.connect_database(config['db_name'], config['db_port_mails'])
    collection = db['mails']

    try:
        collection.create_index('mail', unique=True)
    except pymongo.errors.OperationFailure as e:
        print u'{}'.format(e)
        sys.exit(1)

    api = connect_twitter(config)
    items = get_user_timeline(api, 'checkmydump')
    content = iterate_items(items)

    mail_address_list = mh.extract_mail_address(''.join(content))

    for mail_address in mail_address_list:
        mail_address = uh.handle_unicode(mail_address.strip().lower())
        insert_one(collection, mail_address, 'pastebin.com')



if __name__ == '__main__':
    main()
