# coding:utf-8
"""Some function to generate code."""
import random
import time
import string
import hmac
from hashlib import md5

from config import CFG as O_O

pool = string.ascii_letters + string.digits


def rand6():
    return ''.join(random.choice(pool) for _ in range(6))


def rand12():
    rand = ''.join(random.choice(pool) for _ in range(8))
    stamp = hex(int(time.time()))[-4:]
    return rand + stamp


def encode_passwd(passwd):
    return hmac.new(O_O.server.pass_mixin.encode('utf-8'),
                    passwd.encode()).hexdigest()


def encode_msg(code, timestamp, user_id):
    return hmac.new(code.encode(),
                    (str(timestamp) + str(user_id)).encode()).hexdigest()


def create_random_code():
    """Create a random code with time and md5."""
    return md5(str(time.time()).encode()).hexdigest()


def generate_id(namespace='0000'):
    """Create an ID."""
    timep = hex(int(time.time() * 1000))[2:]
    rands = f'{random.randint(0, 65536):04x}'
    return f'{namespace}-{timep[4:8]}-{timep[:4]}-{rands}-{timep[8:]}'
