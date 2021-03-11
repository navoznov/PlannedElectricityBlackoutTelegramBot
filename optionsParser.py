#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt
from options import Options


def parse():
    try:
        longopts = ['bot-token=', 'admin-ids=']
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv, 't:a', longopts)
        args = {}
        for a, v in opts:
            aa = a.replace('--', '')
            args[aa] = v
    except getopt.GetoptError as e:
        sys.exit(2)

    telegram_bot_token = args.get('bot-token', None)
    return Options(telegram_bot_token)