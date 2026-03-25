#! /usr/bin/env python3
"""
usage: python create_config.py
description: Creates  ~/.config/picas/conf.yml containing encrypted authentication to Picas DB
"""
import os
from pathlib import Path
import getpass

homedir = Path.home()
Path(os.path.join(homedir, "config", "picas")).mkdir(parents=True, exist_ok=True)
db_database = getpass.getpass("Enter the picas database name: ")
db_username = getpass.getpass("Enter the picas database username: ")
db_password = getpass.getpass("Enter the picas database password: ")

os.system(f'picas-cli init --host-url https://picas.surfsara.nl:6984 --database {db_database} --username {db_username} --password {db_password}')