#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import pymongo
from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)


def isvalid_md5(hash_string):
    p = re.compile(r'^[a-f0-9]{32}$')
    return p.match(hash_string.lower())


def isvalid_sha1(hash_string):
    p = re.compile(r'^[a-f0-9]{40}$')
    return p.match(hash_string.lower())


def isvalid_sha224(hash_string):
    p = re.compile(r'^[a-f0-9]{56}$')
    return p.match(hash_string.lower())


def isvalid_sha256(hash_string):
    p = re.compile(r'^[a-f0-9]{64}$')
    return p.match(hash_string.lower())


def isvalid_sha384(hash_string):
    p = re.compile(r'^[a-f0-9]{96}$')
    return p.match(hash_string.lower())


def isvalid_sha512(hash_string):
    p = re.compile(r'^[a-f0-9]{128}$')
    return p.match(hash_string.lower())


def connect_database():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    return client.hashes


@app.route('/')
def show_homepage():
    return render_template('home.html', hashes = 10)


@app.route('/legal')
def show_legal():
    return render_template('legal.html')


@app.route('/privacy')
def show_privacy():
    return render_template('privacy.html')


@app.route('/mail', methods=['GET'])
def show_mail_address_list():
    try:
        param_skip = int(request.args.get('skip'))
    except (ValueError, TypeError) as e:
        param_skip = 0

    try:
        param_limit = int(request.args.get('limit'))
    except (ValueError, TypeError) as e:
        param_limit = 10

    db = connect_database()
    collection = db.mail_address

    result_string = list(collection.find({}).skip(param_skip).limit(param_limit))
    return render_template('mail.html', mail_address_list = result_string, isvisible = True)


@app.route('/mail/q/<param_query>', methods=['GET'])
def show_mail_address(param_query):
    try:
        param_skip = int(request.args.get('skip'))
    except (ValueError, TypeError) as e:
        param_skip = 0

    try:
        param_limit = int(request.args.get('limit'))
    except (ValueError, TypeError) as e:
        param_limit = 10

    db = connect_database()
    collection = db.mail_address

    result_string = list(collection.find({}).skip(param_skip).limit(param_limit))
    return render_template('mail.html', mail_address_list = result_string, isvisible = True)


@app.route('/hash/decrypt', methods=['GET'])
def show_hash_list():
    try:
        param_skip = int(request.args.get('skip'))
    except (ValueError, TypeError) as e:
        param_skip = 0

    try:
        param_limit = int(request.args.get('limit'))
    except (ValueError, TypeError) as e:
        param_limit = 10

    db = connect_database()
    collection = db.password

    hashes_list = list(collection.find().skip(param_skip).limit(param_limit))
    return render_template('hash.html', hashes = hashes_list, isvisible = True)


@app.route('/hash/decrypt/search', methods=['GET'])
def show_hash():
    db = connect_database()
    collection = db.password

    try:
        param_query = request.args.get('q')
    except (ValueError, TypeError) as e:
        param_query = ''

    md5 = isvalid_md5(param_query)
    sha1 = isvalid_sha1(param_query)
    sha224 = isvalid_sha224(param_query)
    sha256 = isvalid_sha256(param_query)
    sha384 = isvalid_sha384(param_query)
    sha512 = isvalid_sha512(param_query)

    if md5:
        result_string = list(collection.find({ 'hash.md5': md5.group(0) }))
    elif sha1:
        result_string = list(collection.find({ 'hash.sha1': sha1.group(0) }))
    elif sha224:
        result_string = list(collection.find({ 'hash.sha224': sha224.group(0) }))
    elif sha256:
        result_string = list(collection.find({ 'hash.sha256': sha256.group(0) }))
    elif sha384:
        result_string = list(collection.find({ 'hash.sha384': sha384.group(0) }))
    elif sha512:
        result_string = list(collection.find({ 'hash.sha512': sha512.group(0) }))
    else:
        result_string = list(collection.find({ 'password': param_query }))

    return render_template('hash.html', hashes = result_string, isvisible = True)


if __name__ == '__main__':
    app.run()
