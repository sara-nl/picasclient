import os
import yaml
import getpass
from jsonschema import validate, ValidationError


class PicasConfigSchemaError(Exception):
    """
    Exception raised for schema validation errors in the PicasConfig.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


PICAS_CONFIG_SCHEMA = {
    'type': 'object',
    'properties': {
        'host_url': {
            'type': 'string',
            'default': 'http://localhost:5984',
            'description': 'URL of the CouchDB server'
        },
        'database': {
            'type': 'string',
            'default': 'mypicasdb',
            'description': 'Name of the CouchDB database to use'
        },
        'username': {
            'type': 'string',
            'default': None,
            'description': 'Username for CouchDB'
        },
        'password': {
            'type': 'string',
            'default': None,
            'description': 'Password for CouchDB, if it is not set it will be prompted'
        }
    },
    'required': ['host_url', 'database', 'username', 'password'],
    'additionalProperties': False
}

class PicasConfig:
    """
    Handle the configuration for Picas.
    """
    def __init__(self, config_path=None, load=True) -> None:
        """
        Initialize the PicasConfig with a path to the configuration file.

        :param config_path: Path to the configuration file, defaults to '~/.config/picas/conf.yml'
        :param load: Whether to load the configuration immediately, defaults to True
        """
        self.config_path = config_path or '~/.config/picas/conf.yml'
        self.config = {}

        if load:
            self.load_config()

    def validate_config(self, config=None):
        """
        Validate the current configuration against the schema.
        Raises PicasConfigSchemaError if validation fails.
        """
        try:
            validate(instance=config or self.config, schema=PICAS_CONFIG_SCHEMA)
            print("Configuration validation passed.")
        except ValidationError as exc:
            raise PicasConfigSchemaError(f"Configuration validation failed: {exc.message}")

    def load_config(self):
        """
        Load the configuration yaml file from the specified path and validate against schema.
        """
        print(f"load the configuration from {self.config_path}")
        expanded_path = os.path.expanduser(self.config_path)

        if not os.path.exists(expanded_path):
            raise FileNotFoundError(f"configuration file not found: {self.config_path}")

        with open(expanded_path, 'r') as fobj:
            self.config = yaml.safe_load(fobj)

        self.validate_config()

    def save_config(self, args):
        """
        Save the current configuration to the specified path.
        """
        print(f"save the configuration to {self.config_path}")

        self.config['host_url'] = args.host_url
        self.config['database'] = args.database
        self.config['username'] = args.username

        # if the password is not set, it will be prompted, do not echo it
        if args.password is None:
            args.password = getpass.getpass(
                f"enter the CouchDB password for the account "
                f"'{args.username}' and database '{args.database}': ")
        self.config['password'] = args.password


        expanded_path = os.path.expanduser(self.config_path)

        # make the config directory if it does not exist
        config_dir = os.path.dirname(expanded_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        self.validate_config()

        # write the configuration to the file
        config_path = expanded_path
        with open(config_path, 'w') as fobj:
            yaml.safe_dump(self.config, fobj, default_flow_style=False)
