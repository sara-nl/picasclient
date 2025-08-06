import os
import yaml
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
    def __init__(self, config_path=None) -> None:
        """
        Initialize the PicasConfig with a path to the configuration file.

        :param config_path: Path to the configuration file, defaults to '~/.config/picas/conf.yml'
        """
        self.config_path = config_path or '~/.config/picas/conf.yml'
        self.config = {}

        self.load_config()

    def load_config(self):
        """
        Load the configuration yaml file from the specified path and validate against schema.
        """
        print(f"Loading configuration from {self.config_path}")
        expanded_path = os.path.expanduser(self.config_path)

        if not os.path.exists(expanded_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(expanded_path, 'r') as fobj:
            self.config = yaml.safe_load(fobj)

        # validate configuration against schema
        try:
            validate(instance=self.config, schema=PICAS_CONFIG_SCHEMA)
            print("Configuration validation passed.")
        except ValidationError as exc:
            raise PicasConfigSchemaError(f"Configuration validation failed: {exc.message}")

    def save_config(self, args):
        """
        Save the current configuration to the specified path.
        """
        # Implementation to save the configuration file
        print(f"Saving configuration to {self.config_path}")