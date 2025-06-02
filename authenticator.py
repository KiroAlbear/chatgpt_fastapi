import base64
import hashlib
import hmac
import struct
import time

FILE_NAME = 'secrets.txt'
ENCODING = 'utf-8'


def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
    return h


def get_totp_token(secret):
    return str(get_hotp_token(secret, intervals_no=int(time.time()) // 30)).zfill(6)



def add_new_secrets(secretKeyParam:str):

    try:
        return get_totp_token(secretKeyParam)
    except Exception as e:
        print('Invalid secret key {}'.format(e))
        return

    
