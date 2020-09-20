#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import pymongo
import locale

from flask import Flask, abort, request, jsonify, render_template
from flask_cassandra import CassandraCluster

from cassandra.query import SimpleStatement

from influxdb import InfluxDBClient
from datetime import datetime


locale.setlocale(locale.LC_ALL, '')
app = Flask(__name__, static_url_path='')
app.config.from_json('config.json')
cassandra = CassandraCluster()


def connect_cassandra():
    session = cassandra.connect()
    session.set_keyspace('leakz')

    return session


with app.app_context():
    session = connect_cassandra()


def make_response(documents):
    results = []

    for document in documents:
        results.append({
            'passphrase': document.passphrase,
            'hash': {
                'md5': document.md5,
                'sha1': document.sha1,
                'sha224': document.sha224,
                'sha256': document.sha256,
                'sha384': document.sha384,
                'sha512': document.sha512,
                'ntlm': document.ntlm
            }
        })

    return jsonify(results)


@app.route('/beta/explore')
def explore_cassandra_documents():
    statement = SimpleStatement('SELECT * FROM leakz.leakz_model LIMIT 50')
    documents = session.execute(statement)

    return make_response(documents)


@app.route('/beta/lookup/<passphrase>')
def lookup_cassandra_document(passphrase):
    statement = 'SELECT * FROM leakz.leakz_model WHERE passphrase=?'
    prepare = session.prepare(statement)
    documents = session.execute(prepare, [passphrase])

    return make_response(documents)


def connect_mongodb(database, secret, port='27017', server='127.0.0.1'):
    client = pymongo.MongoClient('mongodb://{}:{}/'.format(server, port),
                                 username='pymongo',
                                 password=secret,
                                 authSource=database,
                                 authMechanism='SCRAM-SHA-1')

    return client[database]


def get(iterable, keys):
    try:
        result = iterable

        for key in keys:
            result = result[key]

        return result

    except (KeyError, IndexError):
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


def api_search_hash(collection, param_query):
    key, hash = guess_hash(param_query)

    try:
        return list(collection.find({key: hash}, {'_id': 0, 'password': 1}))[0]
    except IndexError:
        return []


def api_search_password(collection, param_query):
    key, hash = guess_hash(param_query)

    try:
        condition = {'_id': 0, 'password': 0}
        return list(collection.find({key: hash}, condition))[0]['hash']
    except IndexError:
        return []


def api_search_mail(collection, param_query):
    try:
        result = list(collection.find(
            {'mail': param_query}, {'_id': 0, 'mail': 0}))[0]
        return {
            'leaked': ', '.join(result['leak'])
        }
    except IndexError:
        return []


def handle_pagination(param_skip, param_limit):
    if param_skip == 0:
        param_skip = 10

    entries = list(
        range(param_skip, (param_skip + param_limit * 8), param_limit))
    last_entry = (entries[-1] + param_limit)

    if entries[-1] <= 80:
        first_entry = 0
    else:
        first_entry = (entries[-1] - 80)

    return first_entry, last_entry, entries


def match_mail_address(document):
    return re.match(r'\b[\w.+-]+?@[-_\w]+[.]+[-_.\w]+\b', document)


@app.route('/', methods=['GET'])
def show_homepage():
    db = connect_mongodb(
        app.config['MONGO_DB'], app.config['MONGO_PASSWORD'],
        app.config['MONGO_PORT'], app.config['MONGO_URI'])

    amount_hashes = db['passwords'].estimated_document_count()
    amount_mails = db['mails'].estimated_document_count()

    return render_template('home.j2',
                           amount_hashes='{:n}'.format(amount_hashes),
                           amount_mails='{:n}'.format(amount_mails),
                           title='Lookup your hashed password',
                           searchform_visible=True,
                           alert_visible=True)


@app.route('/api', methods=['GET'])
def show_api():
    return render_template('api.j2', menu_is_active='api')


@app.route('/legal', methods=['GET'])
def show_legal():
    return render_template('legal.j2')


@app.route('/privacy', methods=['GET'])
def show_privacy():
    return render_template('privacy.j2')


@app.route('/explore', methods=['GET'])
def show_hash_list():
    db = connect_mongodb(
        app.config['MONGO_DB'], app.config['MONGO_PASSWORD'],
        app.config['MONGO_PORT'], app.config['MONGO_URI'])
    collection = db['passwords']

    try:
        param_skip = int(request.args.get('skip'))
    except (ValueError, TypeError):
        param_skip = 0

    try:
        param_limit = int(request.args.get('limit'))

        if param_limit > 200:
            param_limit = 200

    except (ValueError, TypeError):
        param_limit = 10

    pagination_list = handle_pagination(param_skip, param_limit)
    result_list = list(collection.find().skip(
        param_skip).limit(param_limit).sort([('$natural', -1)]))

    return render_template('explore.j2',
                           result_type='hash',
                           url='/explore',
                           menu_is_active='explore',
                           result_list=result_list,
                           entries=pagination_list[2],
                           last_entry=pagination_list[1],
                           first_entry=pagination_list[0])


@app.route('/api/hash/<param_query>', methods=['GET'])
def api_query_hash(param_query):
    influx_client = InfluxDBClient(
        app.config['INFLUX_URI'], app.config['INFLUX_PORT'],
        'root', 'root', app.config['INFLUX_DB'])
    influx_client.create_database(app.config['INFLUX_DB'])

    db = connect_mongodb(
        app.config['MONGO_DB'], app.config['MONGO_PASSWORD'],
        app.config['MONGO_PORT'], app.config['MONGO_URI'])
    collection = db['passwords']

    data = api_search_hash(collection, param_query)

    influx_json_body = [{
        'measurement': 'api_endpoint_short',
        'tags': {
            'endpoint': 'hash'
        },
        'time': datetime.utcnow(),
        'fields': {
            'status': 200 if data else 404,
            'value': param_query.lower()
        }
    }]

    influx_client.write_points(influx_json_body)

    if data:
        return jsonify(data)
    else:
        return abort(404)


@app.route('/api/password/<param_query>', methods=['GET'])
def api_query_password(param_query):
    influx_client = InfluxDBClient(
        app.config['INFLUX_URI'], app.config['INFLUX_PORT'],
        'root', 'root', app.config['INFLUX_DB'])
    influx_client.create_database(app.config['INFLUX_DB'])

    db = connect_mongodb(
        app.config['MONGO_DB'], app.config['MONGO_PASSWORD'],
        app.config['MONGO_PORT'], app.config['MONGO_URI'])
    collection = db['passwords']

    data = api_search_password(collection, param_query)

    influx_json_body = [{
        'measurement': 'api_endpoint_short',
        'tags': {
            'endpoint': 'password'
        },
        'time': datetime.utcnow(),
        'fields': {
            'status': 200 if data else 404,
            'value': param_query
        }
    }]

    influx_client.write_points(influx_json_body)

    if data:
        return jsonify(data)
    else:
        return abort(404)


@app.route('/api/mail/<param_query>', methods=['GET'])
def api_query_mail(param_query):
    influx_client = InfluxDBClient(
        app.config['INFLUX_URI'], app.config['INFLUX_PORT'],
        'root', 'root', app.config['INFLUX_DB'])
    influx_client.create_database(app.config['INFLUX_DB'])

    db = connect_mongodb(
        app.config['MONGO_DB'], app.config['MONGO_PASSWORD'],
        app.config['MONGO_PORT'], app.config['MONGO_URI'])
    collection = db['mails']

    data = api_search_mail(collection, param_query)

    influx_json_body = [{
        'measurement': 'api_endpoint_short',
        'tags': {
            'endpoint': 'mail'
        },
        'time': datetime.utcnow(),
        'fields': {
            'status': 200 if data else 404,
            'value': param_query.lower()
        }
    }]

    influx_client.write_points(influx_json_body)

    if data:
        return jsonify(data)
    else:
        return abort(404)


@app.route('/hash/<param_query>', methods=['GET'])
def show_hash_value(param_query):
    influx_client = InfluxDBClient(
        app.config['INFLUX_URI'], app.config['INFLUX_PORT'],
        'root', 'root', app.config['INFLUX_DB'])
    influx_client.create_database(app.config['INFLUX_DB'])

    db = connect_mongodb(
        app.config['MONGO_DB'], app.config['MONGO_PASSWORD'],
        app.config['MONGO_PORT'], app.config['MONGO_URI'])
    col_password = db['passwords']

    result_list = search_hash_or_password(col_password, param_query)
    result_type = 'hash'

    influx_json_body = [{
        'measurement': 'api_endpoint_short',
        'tags': {
            'endpoint': 'hash'
        },
        'time': datetime.utcnow(),
        'fields': {
            'status': 200 if len(result_list) > 0 else 404,
            'value': param_query.lower()
        }
    }]

    influx_client.write_points(influx_json_body)

    return render_template('home.j2',
                           title='Detailed information',
                           result_list=result_list,
                           result_type=result_type,
                           param_query=param_query,
                           searchform_visible=False,
                           pagination_visible=False)


@app.route('/search', methods=['GET'])
def show_hash():
    influx_client = InfluxDBClient(
        app.config['INFLUX_URI'], app.config['INFLUX_PORT'],
        'root', 'root', app.config['INFLUX_DB'])
    influx_client.create_database(app.config['INFLUX_DB'])

    db = connect_mongodb(
        app.config['MONGO_DB'], app.config['MONGO_PASSWORD'],
        app.config['MONGO_PORT'], app.config['MONGO_URI'])
    col_password = db['passwords']
    col_mail = db['mails']

    try:
        param_query = request.args.get('q')
    except (ValueError, TypeError):
        param_query = ''

    if match_mail_address(param_query):
        result_list = list(col_mail.find({'mail': param_query}))
        result_type = 'mail'
    else:
        result_list = search_hash_or_password(col_password, param_query)
        result_type = 'hash'

    return render_template('home.j2',
                           result_list=result_list,
                           result_type=result_type,
                           param_query=param_query,
                           title='Lookup your hashed password',
                           pagination_visible=False,
                           searchform_visible=True)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
