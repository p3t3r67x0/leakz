#!/usr/bin/env python

import sys
import math
import multiprocessing
import add_password
import argparse

import utils.database_helper as dbh
import utils.password_handling as ph
import utils.file_hadndling as fh
import utils.unicode_helper as uh
import utils.mail_handling as mh


def worker(passwords, args):
    db = dbh.connect_database('hashes', args.port)
    collection = db['passwords']

    try:
        collection.create_index("password", unique=True)
        collection.create_index("hash.md5", unique=True)
        collection.create_index("hash.sha1", unique=True)
        collection.create_index("hash.sha224", unique=True)
        collection.create_index("hash.sha256", unique=True)
        collection.create_index("hash.sha384", unique=True)
        collection.create_index("hash.sha512", unique=True)
    except pymongo.errors.OperationFailure as e:
        print e
        sys.exit(1)

    for password in passwords:
        password = password.strip().replace(' ', '')

        if password and not mh.extract_mail_address(password):
            password_string = uh.handle_unicode(password)

            if len(password_string) > 3 and len(password_string) < 24:
                hash_string = ph.hash_password(password)
                add_password.insert_one(
                    collection, password_string, hash_string)

    return


def main():
    parser = argparse.ArgumentParser(
        description='Add passwords from file to your mongodb instance')
    parser.add_argument('-f, --file', metavar='F', required=True, dest='file',
                        help='file with absolute or relative path')
    parser.add_argument('-p, --port', metavar='P', required=True, dest='port',
                        help='define mongodb port to connect the database')

    args = parser.parse_args()
    passwords = fh.load_document(args.file)
    core_count = multiprocessing.cpu_count()
    chunk_size = int(math.ceil(len(passwords) / core_count))

    for i in xrange(core_count):
        job = passwords[i * chunk_size:(i + 1) * chunk_size]
        p = multiprocessing.Process(target=worker, args=(job, args,))
        p.start()


if __name__ == '__main__':
    main()
