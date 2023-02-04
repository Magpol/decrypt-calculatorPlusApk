#!/usr/bin/env python
# Bruteforce password from Calculator+ - https://github.com/Magpol
import argparse
from Crypto.Hash import MD5

def get_faulty_hex_string(digits):
    # DONT DO THIS.. PLEASE
    faulty_md5_hex_string = ""
    length = len(digits) - 1
    if length >= 0:
        i = 0
        while True:
            i2 = i + 1
            faulty_md5_hex_string += f'{digits[i] & 255:x}'
            if i2 > length:
                break
            i = i2
    return faulty_md5_hex_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Bruteforce the password for Android app eztools.calculator.photo.vault")
    parser.add_argument("--hash", "-H", type=str,
                        required=True, help="Extracted MD5 hash")
    args = parser.parse_args()

    # We do not need 0000 because leading 0 is not allowed by the app
    for i in range(1000, 10000):
        h = MD5.new()
        h.update(str(i).encode("UTF-8"))
        if get_faulty_hex_string(h.digest()) == args.hash:
            print(f'Found password: %d' % i)