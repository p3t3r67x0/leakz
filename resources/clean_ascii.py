#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import utils.file_handling as fh


def replace_ascii(text):
    pattern = {
        'ô': 'Ã´',
        'š': 'Å¡',
        '¤': 'Â¤',
        'ö': 'Ã¶',
        'Þ': 'Å¢',
        '¦': 'Â¦',
        '÷': 'Ã·',
        'þ': 'Å£',
        '§': 'Â§',
        'ú': 'Ãº',
        '?': 'Å¤',
        ' ̈': 'Â ̈',
        'ü': 'Ã¼',
        '?': 'Å¥',
        '©': 'Â©',
        'ý': 'Ã½',
        'Ù': 'Å®',
        '«': 'Â«',
        'Ã': 'Ä‚',
        'ù': 'Å ̄',
        '¬': 'Â¬',
        'ã': 'Äƒ',
        'Û': 'Å°',
        '-': 'Â-',
        '¥': 'Ä„',
        'û': 'Å±',
        '®': 'Â®',
        '¹': 'Ä...',
        '?': 'Å¹',
        '°': 'Â°',
        'Æ': 'Ä†',
        'Ÿ': 'Åº',
        '±': 'Â±',
        'æ': 'Ä‡',
        ' ̄': 'Å»',
        ' ́': 'Â ́',
        'È': 'ÄŒ',
        '¿': 'Å¼',
        'μ': 'Âμ',
        'è': 'Ä?',
        'Ž': 'Å½',
        '¶': 'Â¶',
        'Ï': 'ÄŽ',
        'ž': 'Å¾',
        '·': 'Â·',
        'ï': 'Ä?',
        '¡': 'Ë‡',
        ' ̧': 'Â ̧',
        'Ð': 'Ä?',
        '¢': 'Ë ̃',
        '»': 'Â»',
        'ð': 'Ä‘',
        'ÿ': 'Ë™',
        'Á': 'Ã?',
        'Ê': 'Ä ̃',
        '²': 'Ë›',
        'Â': 'Ã‚',
        'ê': 'Ä™',
        '½': 'Ë?',
        'Ä': 'Ã„',
        'Ì': 'Äš',
        '–': 'â€“',
        'Ç': 'Ã‡',
        'ì': 'Ä›',
        '—': 'â€”',
        'É': 'Ã‰',
        'Å': 'Ä¹',
        '‘': 'â€ ̃',
        'Ë': 'Ã‹',
        'å': 'Äº',
        '’': 'â€™',
        'Í': 'Ã?',
        '¼': 'Ä½',
        '‚': 'â€š',
        'Î': 'ÃŽ',
        '¾': 'Ä¾',
        '“': 'â€œ',
        'Ó': 'Ã“',
        '£': 'Å?',
        '”': 'â€?',
        'Ô': 'Ã”',
        '³': 'Å‚',
        '„': 'â€ž',
        'Ö': 'Ã–',
        'Ñ': 'Åƒ',
        '†': 'â€',
        '×': 'Ã—',
        'ñ': 'Å„',
        '‡': 'â€¡',
        'Ú': 'Ãš',
        'Ò': 'Å‡',
        '•': 'â€¢',
        'Ü': 'Ãœ',
        'ò': 'Åˆ',
        '...': 'â€¦',
        'Ý': 'Ã?',
        'Õ': 'Å?',
        '‰': 'â€°',
        'ß': 'ÃŸ',
        'õ': 'Å‘',
        '‹': 'â€¹',
        'á': 'Ã¡',
        'À': 'Å”',
        '›': 'â€º',
        'â': 'Ã¢',
        'à': 'Å•',
        '€': 'â‚¬',
        'ä': 'Ã¤',
        'Ø': 'Å ̃',
        '™': 'â„¢',
        'ç': 'Ã§',
        'ø': 'Å™',
        'é': 'Ã©',
        'Œ': 'Åš',
        'ë': 'Ã«',
        'œ': 'Å›',
        'í': 'Ã-',
        'ª': 'Åž',
        'î': 'Ã®',
        'º': 'ÅŸ',
        'ó': 'Ã³',
        'Š': 'Å',
        '': 'Â'
    }

    for i in pattern.items():
        text = text.replace(i[1], i[0])
        print(text)

    return text


def main():
    documents = fh.load_document(sys.argv[1])
    lines = []

    for line in documents:
        lines.append(replace_ascii(line.strip()))

    fh.save_document('no_ascii_{}.txt'.format(
        os.path.basename(sys.argv[1])), '\n'.join(lines))


if __name__ == '__main__':
    main()
