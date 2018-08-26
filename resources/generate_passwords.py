#!/usr/bin/env python


import random
import argparse

import utils.file_handling as fh


def generate_leetspeak(password):
    pattern = {'a': '4', 'A': '4', 'b': '8', 'B': '8', 'e': '3', 'E': '3', 'g': '6',
               'G': '6', 'i': '1', 'I': '1', 'o': '0', 'O': '0', 's': '5', 'S': '5',
               't': '7', 'T': '7'}

    for key, value in pattern.iteritems():
        password = password.replace(key, value)

    return password


def generate_year(password):
    passwords = []
    
    if password[-1].isdigit():
        return []

    for year in xrange(1940, 2015):
        passwords.append('{}{}'.format(password, year))

    for year in xrange(00, 99):
        passwords.append('{}{:02}'.format(password, year))

    return passwords


def generate_random(password):
    random_password = list(password)

    for i, e in enumerate(password):
        random_password[i] = random.choice(e.lower() + e.upper())

    return ''.join(random_password)


def main():
    parser = argparse.ArgumentParser(
        description='Generate password combinations from a given string')
    parser.add_argument('-f, --file', metavar='F', required=True, dest='file',
                        help='file with absolute or relative path')
    parser.add_argument('-o, --out', metavar='F', required=True, dest='out',
                        help='output file name, will be saved in same folder')

    args = parser.parse_args()
    documents = fh.load_document(args.file)
    passwords = []

    print '[I] Starting password generation'

    for password in documents:
        passwords = passwords + generate_year(password.strip())
        passwords.append(generate_leetspeak(password.strip()))

    print '[I] Finished password generation'

    output=set(passwords)

    with open(args.out, 'w') as f:
        f.writelines('{}\n'.format(line) for line in output)
        print u'[I] Saved generated passwords in {}'.format(args.out)


if __name__ == '__main__':
    main()
