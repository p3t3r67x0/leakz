#!/usr/bin/env python


import random
import argparse

def load_document(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as e:
        print e
        sys.exit(1)


def generate_leetspeak(password):
    pattern = {'a': '4', 'A': '4', 'b': '8', 'B': '8', 'e': '3', 'E': '3', 'g': '6',
               'G': '6', 'i': '1', 'I': '1', 'o': '0', 'O': '0', 's': '5', 'S': '5',
               't': '7', 'T': '7'}

    for key, value in pattern.iteritems():
        password = password.replace(key, value)

    return password


def generate_year(password):
    result = []

    for i in range(1940, 2005):
        result.append('{}{}'.format(password, i))

    return result


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

    args = parser.parse_args()
    documents = load_document(args.file)
    merged_passwords = []
    leetspeak = []

    print '[I] Starting leetspeak generation'

    for password in documents:
        leetspeak.append(password.strip())

        for i in range(len(password)):
            leetspeak.append(generate_random(password.strip()))

        leetspeak.append(generate_leetspeak(password.strip()))

    print '[I] Finished leetspeak generation'
    print '[I] Starting password appending year generation'

    for password in leetspeak:
        if len(password.strip()) > 0:
            merged_passwords += generate_year(password.strip())

    print '[I] Finished password appending year generation'

    output = set(merged_passwords)

    with open('out.txt', 'w') as f:
        f.writelines('{}\n'.format(line) for line in output)
        print u'[I] Saved generated passwords in out.txt'


if __name__ == '__main__':
    main()
