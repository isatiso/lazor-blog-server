# coding:utf-8
import sys


def dump(sign, *args):
    sys.stdout.write('\n\n' + sign * 80)
    for arg in args:
        sys.stdout.write('\n' + arg)
    sys.stdout.write('\n\n' + sign * 80 + '\n')
    sys.stdout.flush()


def dump_in(*args):
    dump('<', *args)


def dump_out(*args):
    dump('>', *args)


def dump_error(*args):
    dump('%', *args)
