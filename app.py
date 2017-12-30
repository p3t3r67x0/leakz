#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import pymongo
import datetime
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from datetime import datetime

app = Flask(__name__)


@app.template_filter()
def format_time(timestamp):
    return datetime.strptime(timestamp.replace('Z', ''), '%Y%m%d%H%M%S').strftime('%d.%m.%Y %H:%M')


def connect_database(database, port):
    secret = get_secret()
    client = pymongo.MongoClient('mongodb://localhost:{}/'.format(port),
                                 username='pymongo',
                                 password=secret,
                                 authSource=database,
                                 authMechanism='SCRAM-SHA-1')

    return client[database]


def get_secret():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.secret'))
    return load_document(path)[0].strip()


def load_document(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def get(iterable, keys):
    try:
        result = iterable

        for key in keys:
            result = result[key]

        return result

    except (KeyError, IndexError) as e:
        return None


def guess_hash(hash_string):
    m = re.match(r'^[0-9a-fA-F]+$', hash_string)

    if m:
        hash = {
            32: 'hash.md5',
            40: 'hash.sha1',
            56: 'hash.sha224',
            64: 'hash.sha256',
            96: 'hash.sha384',
            128: 'hash.sha512'
        }

        if len(hash_string) in hash:
            return hash[len(hash_string)], hash_string.lower()

    return 'password', hash_string


def search_hash_or_password(collection, param_query):
    key, hash = guess_hash(param_query)

    return list(collection.find({key: hash}, {'_id': 0}))


def handle_pagination(param_skip, param_limit):
    entries = range(param_skip, (param_skip + param_limit * 8), param_limit)
    last_entry = (entries[-1] + param_limit)

    if not entries[0] < 1:
        first_entry = (entries[0] - param_limit)
    else:
        first_entry = 0

    return first_entry, last_entry, entries


def match_mail_address(document):
    return re.match(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', document)


@app.route('/', methods=['GET'])
def show_homepage():
    db = connect_database('hashes', '27017')
    db2 = connect_database('hashes', '27018')
    collection_hash = db.password
    collection_mail = db2.mail_address
    amount_hashes = collection_hash.count()
    amount_mails = collection_mail.count()

    return render_template('home.html',
                           amount_hashes='{:,}'.format(amount_hashes),
                           amount_mails='{:,}'.format(amount_mails),
                           title='Is my mail address leaked?',
                           searchform_visible=True,
                           alert_visible=True)


@app.route('/legal', methods=['GET'])
def show_legal():
    return render_template('legal.html')


@app.route('/privacy', methods=['GET'])
def show_privacy():
    return render_template('privacy.html')


@app.route('/hash/latest', methods=['GET'])
def show_hash_list():
    db = connect_database('hashes', '27017')
    collection = db.password

    try:
        param_skip = int(request.args.get('skip'))
    except (ValueError, TypeError) as e:
        param_skip = 0

    try:
        param_limit = int(request.args.get('limit'))

        if param_limit > 200:
            param_limit = 200

    except (ValueError, TypeError) as e:
        param_limit = 10

    pagination_list = handle_pagination(param_skip, param_limit)
    result_list = list(collection.find().skip(
        param_skip).limit(param_limit).sort([('$natural', -1)]))

    return render_template('latest.html',
                           result_type='hash',
                           url='/hash/latest',
                           menu_is_active='latest',
                           result_list=result_list,
                           entries=pagination_list[2],
                           last_entry=pagination_list[1],
                           first_entry=pagination_list[0])


@app.route('/api/hash/<param_query>', methods=['GET'])
def api_query_hash(param_query):
    db = connect_database('hashes', '27017')
    collection = db.password

    return jsonify(search_hash_or_password(collection, param_query))


@app.route('/hash/<param_query>', methods=['GET'])
def show_hash_value(param_query):
    db = connect_database('hashes', '27017')
    col_password = db.password

    result_list = search_hash_or_password(col_password, param_query)
    result_type = 'hash'

    return render_template('home.html',
                           title='Detailed information',
                           result_list=result_list,
                           result_type=result_type,
                           param_query=param_query,
                           searchform_visible=False,
                           pagination_visible=False)


@app.route('/search', methods=['GET'])
def show_hash():
    db = connect_database('hashes', '27017')
    db2 = connect_database('hashes', '27018')
    col_password = db.password
    col_mail_address = db2.mail_address

    try:
        param_query = request.args.get('q')
    except (ValueError, TypeError) as e:
        param_query = ''

    if match_mail_address(param_query):
        result_list = list(col_mail_address.find({'mail': param_query}))
        result_type = 'mail'
    else:
        result_list = search_hash_or_password(col_password, param_query)
        result_type = 'hash'

    return render_template('home.html',
                           result_list=result_list,
                           result_type=result_type,
                           param_query=param_query,
                           title='Is my mail address leaked?',
                           pagination_visible=False,
                           searchform_visible=True,
                           search_visible=True)


@app.route('/api/cert/<param_query>', methods=['GET'])
def api_query_cert(param_query):
    db = connect_database('hashes', '27017')
    collection = db.cert

    result_list = list(collection.find(
        {'subject.common_name': param_query}, {'_id': 0}))

    if len(result_list) == 0:
        return 'ERROR no result was found'

    return render_template('certificate.html',
                           result_list=result_list)


@app.route('/cert', methods=['GET'])
def find_all_cert():
    db = connect_database('hashes', '27017')
    collection = db.cert

    result_list = list(collection.find(
        {}, {'_id': 0, 'subject.common_name': 1, 'hash_values.md5': 1, 'valid_not_before': 1, 'valid_not_after': 1}))
    return render_template('cert_overview.html',
                           result_list=result_list)


if __name__ == '__main__':
    app.run(debug=True)
