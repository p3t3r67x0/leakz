#!/usr/bin/env python

import sys
import math
import json
import multiprocessing
import add_password
import argparse

import utils.database_helper as dbh
import utils.password_handling as ph
import utils.unicode_helper as uh
import utils.file_handling as fh
import utils.mail_handling as mh


def worker(passwords, args):
    config = json.loads(fh.get_config())
    db = dbh.connect_database(config['db_name'], config['db_port_passwords'])
    collection = db['passwords']

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

    args = parser.parse_args()
    passwords = fh.load_document(args.file)
    core_count = multiprocessing.cpu_count()
    chunk_size = int(math.ceil(len(passwords) / core_count) - 2)

    for i in xrange(core_count):
        job = passwords[i * chunk_size:(i + 1) * chunk_size]
        p = multiprocessing.Process(target=worker, args=(job, args,))
        p.start()


if __name__ == '__main__':
    main()
