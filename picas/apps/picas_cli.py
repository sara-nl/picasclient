import sys
import argparse
from argparse import RawTextHelpFormatter
import yaml

from picas.picas_config import PicasConfig, PicasConfigSchemaError, decrypt_password

# .. todo:: use the picas logger instead of print statements

def parse_args() -> argparse.ArgumentParser:
    """
    Define the parser for the exec script
    """

    parser = argparse.ArgumentParser(
        description=(
            "The picas command line client\n"
            "Usage example\n"
            "Initialize the picas configuration, create the ~/.config/picas/conf.yml\n"
            "   $ picas init \n"
            "Change the picas couch db password\n"
            "   $ picas passwd"
        ),
        formatter_class=RawTextHelpFormatter
    )

    parser.add_argument(
        '--config',
        type=str,
        default='~/.config/picas/conf.yml',
        help='Path to the picas configuration file',
        dest='config_path'
    )

    subparsers = parser.add_subparsers(help='these are the supported verbs/actions')

    #
    # define the sub-parser for initializing the picas configuration
    #
    parser_init = subparsers.add_parser(
        'init',
        help='Initialize the picas configuration',
    )
    parser_init.set_defaults(func=initialize_picas_configuration)

    parser_init.add_argument(
        '--host-url',
        type=str,
        default='http://localhost:5984',
        help='URL of the CouchDB server',
        dest='host_url'
    )

    parser_init.add_argument(
        '--database',
        type=str,
        default='mypicasdb',
        help='Name of the CouchDB database to use',
        dest='database'
    )

    parser_init.add_argument(
        '--username',
        type=str,
        default=None,
        help='Username for CouchDB',
        dest='username'
    )

    parser_init.add_argument(
        '--password',
        type=str,
        default=None,
        help='Password for CouchDB, if it is not set it will be prompted',
        dest='password'
    )

    #
    # end define the sub-parser for initializing the picas configuration
    #

    #
    # define the sub-parser for changing the picas couch db password
    #
    parser_passwd = subparsers.add_parser(
        'passwd',
        help='Change the picas couch db password',
    )
    parser_passwd.set_defaults(func=change_picas_password)

    parser_passwd.add_argument(
        '--new-password',
        type=str,
        default=None,
        help='New password for CouchDB, if it is not set it will be prompted',
        dest='new_password'
    )
    #
    # end define the sub-parser for changing the picas couch db password
    #

    #
    # define the sub-parser for dumping the picas configuration
    #
    parser_dump = subparsers.add_parser(
        'dump-config',
        help='Dump (print) the current picas configuration (redacting secrets)',
    )

    parser_dump.add_argument(
        '--config',
        type=str,
        default='~/.config/picas/conf.yml',
        help='Path to the picas configuration file',
        dest='config_path'
    )
    parser_dump.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file path. If not specified, prints to stdout',
        dest='output_file'
    )
    parser_dump.set_defaults(func=dump_picas_config)
    #
    # end define the sub-parser for dumping the picas configuration
    #
    return parser


def initialize_picas_configuration(parsed_args, *args, **kwargs):
    """
    Function that initializes the picas configuration
    """
    print('initialize the picas configuration...')
    picas_config = PicasConfig(
        config_path=parsed_args.config_path,
        load=False)

    picas_config.save_config(parsed_args)


def change_picas_password(parsed_args, *args, **kwargs):
    """
    Function that changes the picas couch db password
    """
    print('changing picas couch db password...')

    picas_config = PicasConfig(config_path=parsed_args.config_path)
    picas_config.change_password(parsed_args)

def dump_picas_config(parsed_args, *_, **__):
    """
    Generate and print a picasconfig.py script based on the existing conf.yml.
    Decrypts the stored encrypted password if available.
    """
    config_path = getattr(parsed_args, 'config_path', '~/.config/picas/conf.yml')
    output_file = getattr(parsed_args, 'output_file', None)

    try:
        cfg = PicasConfig(config_path=config_path, load=True)
    except FileNotFoundError as exc:
        print(f"[picas] config file not found: {exc}", file=sys.stderr)
        sys.exit(1)
    except PicasConfigSchemaError as exc:
        print(f"[picas] config schema error: {exc}", file=sys.stderr)
        sys.exit(1)

    host = cfg.config.get('host_url', '')
    db = cfg.config.get('database', '')
    user = cfg.config.get('username', '')
    enc = cfg.config.get('encrypted_password')

    if enc:
        try:
            plain_pwd = decrypt_password(enc).decode('utf-8')
        except Exception:
            plain_pwd = '<could-not-decrypt>'
    else:
        plain_pwd = '<no-password>'

    script = f"""# Autogenerated from {config_path}
PICAS_HOST_URL = {host!r}
PICAS_DATABASE = {db!r}
PICAS_USERNAME = {user!r}
PICAS_PASSWORD = {plain_pwd!r}
"""

    if output_file:
        import os
        output_path = os.path.expanduser(output_file)
        try:
            with open(output_path, 'w') as f:
                f.write(script)
            print(f"Configuration dumped to {output_path}")
        except IOError as e:
            print(f"[picas] error writing to file {output_path}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(script.rstrip())

def main():

    arg_parser = parse_args()
    args = arg_parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)


if __name__ == "__main__":
    main()
