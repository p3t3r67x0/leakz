#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import json
import asyncio

import utils.file_handling as fh

from couchbase.cluster import Cluster, ClusterOptions, PasswordAuthenticator
from couchbase.search import QueryStringQuery, SearchOptions


async def connect_couchdb(uri, username, password, database):
    auth = PasswordAuthenticator(username, password)
    cluster = Cluster(uri, ClusterOptions(auth))

    result = cluster.search_query('fulltext_idx', QueryStringQuery(
        sys.argv[1]), SearchOptions(skip=0, limit=20))

    rows = cluster.query('select * from leakz use keys [{}]'.format(
        ','.join(['\"{}\"'.format(k.id) for k in result]))).execute()

    for row in rows:
        print(row['leakz']['password'])


if __name__ == '__main__':
    config = json.loads(fh.get_config())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_couchdb(
        config['COUCH_URI'], config['COUCH_USERNAME'],
        config['COUCH_PASSWORD'], config['COUCH_DATABASE']))
