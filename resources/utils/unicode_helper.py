#!/usr/bin/env python
# -*- coding: utf-8 -*-


def handle_unicode(password):
    try:
        password_string = password.decode('utf-8')
    except UnicodeDecodeError as e:
            password_string = password.encode('utf-8')
    except UnicodeEncodeError as e:
            password_string = password.encode('ascii', 'ignore')

    return password_string
