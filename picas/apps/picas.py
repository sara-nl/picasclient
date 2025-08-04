import sys
import argparse
from argparse import RawTextHelpFormatter


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
        '--config',
        type=str,
        default='~/.config/picas/conf.yml',
        help='Path to the picas configuration file',
        dest='config_path'
    )

    parser_init.add_argument(
        '--host-url',
        type=str,
        default='http://localhost:5984',
        help='URL of the CouchDB server',
        dest='host_url'
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

    #
    # end define the sub-parser for changing the picas couch db password
    #

    return parser


def initialize_picas_configuration(parsed_args, *args, **kwargs):
    """
    Function that initializes the picas configuration
    """
    print('Initializing picas configuration...')


def change_picas_password(parsed_args, *args, **kwargs):
    """
    Function that changes the picas couch db password
    """
    print('Changing picas couch db password...')


def main():

    arg_parser = parse_args()
    args = arg_parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)


if __name__ == "__main__":
    main()
