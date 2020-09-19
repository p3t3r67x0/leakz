#!/usr/bin/env python

import sys
import math
import json
import multiprocessing
import add_password
import argparse

import utils.database_helper as dbh
import utils.password_handling as ph
import utils.file_handling as fh
import utils.mail_handling as mh


def worker(passwords, args):
    config = json.loads(fh.get_config())
    db = dbh.connect_mongodb(config['MONGO_DB'], config['MONGO_PORT'], config['MONGO_PASSWORD'])
    collection = db['passwords']

    for password in passwords:
        password = password.strip().replace(' ', '')

        if password and not mh.extract_mail_address(password):
            password_string = password

            if len(password_string) > 3 and len(password_string) < 32 and not ph.test_md5(password_string):
                hash_string = ph.hash_password(password_string)
                add_password.insert_one(collection, password_string, hash_string)

    return


def main():
    parser = argparse.ArgumentParser(
        description='Add passwords from file to your mongodb instance')
    parser.add_argument('-f, --file', metavar='F', required=True, dest='file',
                        help='file with absolute or relative path')

    args = parser.parse_args()
    passwords = fh.load_document(args.file)
    core_count = multiprocessing.cpu_count()
    chunk_size = int(math.ceil(len(passwords) / core_count) - 2)

    for i in range(core_count):
        job = passwords[i * chunk_size:(i + 1) * chunk_size]
        p = multiprocessing.Process(target=worker, args=(job, args,))
        p.start()


if __name__ == '__main__':
    main()
