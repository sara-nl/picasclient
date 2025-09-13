#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adds support for saving the picas password encrypted.
To use it, use the decrypt_password function the password line in your private picasconfig.py.
You can use the encrypt_password command to create a corresponding line for your password.
The key to encrypt your password can be created with keygen.py.

@author: Andreas Schneider <a.schneider@sron.nl>
"""
import os
import stat

from cryptography.fernet import Fernet
import json

CRYPTO_KEY_PATH = os.path.expanduser("~/.config/picas/key.dat")

def generate_and_save_key(key_path=CRYPTO_KEY_PATH, skip_if_exists=True):
    """
    Generate a new Fernet key and saves it to the specified path.

    It will create the directory if it doesn't exist and set appropriate permissions.
    It will also prompt the user before overwriting an existing key.
    """
    # if the key should not be generated if it exists
    if skip_if_exists and os.path.exists(key_path):
        print(f"key already exists at {key_path}. skipping key generation.")
        return

    # generate a random key for encrypting / decrypting data
    print("generate a new random key ...")
    key = Fernet.generate_key()

    # if directory does not exist yet, create it and set the appropriate permissions accessible
    # by the user only
    key_dir = os.path.dirname(key_path)
    if not os.path.isdir(key_dir):
        print("create the directory", key_dir)
        os.mkdir(key_dir)
        os.chmod(key_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    # check if key file exists.
    if os.path.exists(key_path):
        answer = input(f"Do you want to overwrite your current key in {key_path} (y/N)? ")

        if answer.lower() != "y":
            print("Not overwriting your old key.")
            return

    # write the key to file in binary mode and make it readable/writable by owner only
    with open(key_path, "wb") as fobj:
        print("Writing file", key_path)
        fobj.write(key)
    os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)


def read_key():
    with open(CRYPTO_KEY_PATH, 'rb') as f:
        key = f.read()

    return key


def encrypt_password(password, key=None):
    if key is None: # if key is not given
        key = read_key() # read it in
    crypt_obj = Fernet(key) # create fernet object
    encrypted = crypt_obj.encrypt(password) # encrypt password

    return encrypted


def decrypt_password(encrypted, key=None):
    if key is None:
        key = read_key()
    crypt_obj = Fernet(key)
    password = crypt_obj.decrypt(encrypted)

    return password
