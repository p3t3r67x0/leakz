#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import ssl
import OpenSSL
import pymongo
import argparse
import socket
import errno


def load_document(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def connect_database():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    return client.hashes


def insert_one(collection, post):
    try:
        inserted_id = collection.insert_one(post).inserted_id
        print u'[I] Added {} with id {}'.format(post['subject']['common_name'], inserted_id)
    except pymongo.errors.DuplicateKeyError as e:
        print e


def load_certificate(domain, port=443):
    socket.timeout(3)

    try:
        cert = ssl.get_server_certificate((domain, port))
        return (OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert), cert)
    except (socket.error, socket.gaierror) as e:
        print e
        if e.errno == errno.ECONNREFUSED:
            print 'Connection refused'

        return None


def replace_dns_string(data):
    return data.replace('DNS:', '')


def extract_subject_components(x509):
    subject_components = {}

    for item in x509.get_subject().get_components():
        subject_components[item[0]] = item[1]

    return subject_components


def extract_issuer_components(x509):
    issuer_components = {}

    for item in x509.get_issuer().get_components():
        issuer_components[item[0]] = item[1]

    return issuer_components


def extract_extensions(x509):
    subject_alt_name = []
    extensions = []

    for i in xrange(x509.get_extension_count()):
        extensions.append((x509.get_extension(i).get_short_name(),
                           x509.get_extension(i).__str__()))

    for extension in extensions:
        if extension[0] == 'subjectAltName':
            subject_alt_name = extension[1].split(', ')

    return map(replace_dns_string, subject_alt_name)


def has_expired(x509):
    return x509.has_expired()


def valid_not_before(x509):
    return x509.get_notBefore()


def valid_not_after(x509):
    return x509.get_notAfter()


def extract_signature_algorithm(x509):
    return x509.get_signature_algorithm()


def get_subject_hash(x509):
    return x509.get_subject().hash()


def get_issuer_hash(x509):
    return x509.get_issuer().hash()


def format_hash(hash_value):
    return hash_value.replace(':', '').lower()


def get_hash_values(x509):
    return {'md5': format_hash(x509.digest('md5')),
            'sha1': format_hash(x509.digest('sha1')),
            'sha224': format_hash(x509.digest('sha224')),
            'sha256': format_hash(x509.digest('sha256')),
            'sha384': format_hash(x509.digest('sha384')),
            'sha512': format_hash(x509.digest('sha512'))}


def get_public_key_bits(x509):
    return x509.get_pubkey().bits()


def get_public_key_type(x509):
    return x509.get_pubkey().type()


def is_public_key_only(x509):
    return x509.get_pubkey()._only_public


def is_public_key_initialized(x509):
    return x509.get_pubkey()._initialized


def get_serial_number(x509):
    return x509.get_serial_number()


def get_serial_number_length(x509):
    return x509.get_serial_number().bit_length()


def main():
    parser = argparse.ArgumentParser(
        description='Load url from file to query certificates and add them to your mongodb instance')
    parser.add_argument('-f, --file', metavar='F', required=True, dest='file',
                        help='file with absolute or relative path')

    db = connect_database()
    db.cert.create_index('subject.common_name', unique=True)
    collection = db.cert

    args = parser.parse_args()
    documents = load_document(args.file)

    for document in documents:
        url = document.strip('\n').strip('\r')

        try:
            result = load_certificate(url, 443)
            cert = result[1]
            x509 = result[0]
        except TypeError as e:
            continue

        hash_values = {}
        subject = {}
        issuer = {}

        try:
            subject['common_name'] = extract_subject_components(x509)['CN']
        except KeyError as e:
            pass

        try:
            subject['country_name'] = extract_subject_components(x509)['C']
        except KeyError as e:
            pass

        try:
            subject['state_or_province_name'] = extract_subject_components(x509)['ST']
        except KeyError as e:
            pass

        try:
            subject['locality'] = extract_subject_components(x509)['L']
        except KeyError as e:
            pass

        try:
            subject['organization'] = extract_subject_components(x509)['O']
        except KeyError as e:
            pass

        try:
            subject['organizational_unit'] = extract_subject_components(x509)['OU']
        except KeyError as e:
            pass

        try:
            issuer['common_name'] = extract_issuer_components(x509)['CN']
        except KeyError as e:
            pass

        try:
            issuer['country_name'] = extract_issuer_components(x509)['C']
        except KeyError as e:
            pass

        try:
            issuer['state_or_province_name'] = extract_issuer_components(x509)['ST']
        except KeyError as e:
            pass

        try:
            issuer['locality'] = extract_issuer_components(x509)['L']
        except KeyError as e:
            pass

        try:
            issuer['organization'] = extract_issuer_components(x509)['O']
        except KeyError as e:
            pass

        try:
            issuer['organizational_unit'] = extract_issuer_components(x509)['OU']
        except KeyError as e:
            pass


        subject['alt_names'] = extract_extensions(x509)
        subject['hash'] = get_subject_hash(x509)
        issuer['hash'] = get_issuer_hash(x509)

        post = {
            'cert': cert,
            'issuer': issuer,
            'subject': subject,
            'hash_values': get_hash_values(x509),
            'public_key_bits': get_public_key_bits(x509),
            'public_key_type': get_public_key_type(x509),
            'public_key_only': is_public_key_only(x509),
            'public_key_initialized': is_public_key_initialized(x509),
            'serial_number': str(get_serial_number(x509)),
            'serial_number_length': get_serial_number_length(x509),
            'valid_not_before': valid_not_before(x509),
            'valid_not_after': valid_not_after(x509)
        }

        insert_one(collection, post)


if __name__ == '__main__':
    main()
