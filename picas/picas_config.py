import os
import yaml
import getpass
import requests
import json
from jsonschema import validate, ValidationError

from .crypto import generate_and_save_key, encrypt_password, decrypt_password

# .. todo:: use the picas logger instead of print statements
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
        'encrypted_password': {
            'type': 'string',
            'default': None,
            'description': 'Encrypted password for CouchDB, if it is not set it will be prompted'
        }
    },
    'required': ['host_url', 'database', 'username', 'encrypted_password'],
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

    def __str__(self):
        """
        Return a string representation of the configuration.
        Masks the encrypted password for security.
        """
        if not self.config:
            return "PicasConfig: No configuration loaded"

        # Create a copy of the config to mask sensitive data
        display_config = self.config.copy()
        if 'encrypted_password' in display_config:
            display_config['encrypted_password'] = '***masked***'

        return f"PicasConfig:\n{yaml.dump(display_config, default_flow_style=False, indent=2)}"

    def validate_config(self, config=None):
        """
        Validate the current configuration against the schema.
        Raises PicasConfigSchemaError if validation fails.
        """
        try:
            validate(instance=config or self.config, schema=PICAS_CONFIG_SCHEMA)
            print("configuration validation passed.")
        except ValidationError as exc:
            raise PicasConfigSchemaError(f"configuration validation failed: {exc.message}")

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

        self.config['host_url'] = args.host_url
        self.config['database'] = args.database
        self.config['username'] = args.username

        # setup / check the encryption key
        generate_and_save_key()

        # if the password is not set, it will be prompted, do not echo it
        if args.password is None:
            password = getpass.getpass(
                f"enter the CouchDB password for the account "
                f"'{args.username}' and database '{args.database}': ")
        else:
            password = args.password
        # convert the password to bytes
        if isinstance(password, str):
            password = password.encode('utf-8')

        # encrypt the password
        self.config['encrypted_password'] = encrypt_password(password).decode()

        # test decrypting the password and check if it matches the original
        #_decrypted_password = decrypt_password(self.config['encrypted_password'])
        #if _decrypted_password != password:
        #    breakpoint()
        #    msg = "The decrypted password does not match the original password."
        #    raise ValueError(msg)

        self.write_config(self.config)

    def write_config(self, config):
        """
        Write the provided configuration to the specified path.
        """
        print(f"write the configuration to {self.config_path}")
        self.config = config

        config_path = os.path.expanduser(self.config_path)

        # make the config directory if it does not exist
        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)


        self.validate_config()

        with open(config_path, 'w') as fobj:
            yaml.safe_dump(self.config, fobj, default_flow_style=False)

    def change_couchdb_password(self,
                                uri: str,
                                username: str,
                                old_password: str,
                                new_password: str) -> None:
        """
        Change the CouchDB password on the server.

        The procedure is described in the Picas documentation.
        https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_change_password.html

        That is equivalent to the following curl commands:

        ```bash

        uri=https://picas.surfsara.nl:6984
        username=USERNAME
        password=PASSWORD
        newpassword=NEWPASSWORD
        curl --silent --user "$username:$password" -X GET $uri/_users/org.couchdb.user:$username | \
            jq '._rev' |  \
            curl --user "$username:$password" -X PUT $uri/_users/org.couchdb.user:$username \
                -H "Accept: application/json" \
                -H "Content-Type: application/json" \
                -H "If-Match:$(</dev/stdin)" -d '{"name":"'$username'", "roles":[], "type":"user", "password":"'$newpassword'"}'
        ```

        :param uri: The URI of the CouchDB server.
        :param username: The username for the CouchDB account.
        :param old_password: The current password for the CouchDB account.
        :param new_password: The new password to set for the CouchDB account.
        :raises ValueError: If the password change fails.
        """
        # convert bytes to string if needed
        if isinstance(old_password, bytes):
            old_password = old_password.decode('utf-8')
        if isinstance(new_password, bytes):
            new_password = new_password.decode('utf-8')

        # get the current user document to retrieve _rev
        user_doc_url = f"{uri}/_users/org.couchdb.user:{username}"
        try:
            # retrieve the user document and the revision
            response = requests.get(user_doc_url, auth=(username, old_password), headers={'Accept': 'application/json'})
            response.raise_for_status()

            user_doc = response.json()
            rev = user_doc.get('_rev')
        except requests.exceptions.RequestException as exc:
            raise ValueError(f"Failed to retrieve user document from CouchDB server: {exc}")

        if not rev:
            raise ValueError("Could not retrieve revision from user document")

        # use the new password to update the user document using a put request
        new_user_doc = {
            "name": username,
            "roles": [],
            "type": "user",
            "password": new_password
        }

        try:
            response = requests.put(
                user_doc_url,
                auth=(username, old_password),
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'If-Match': rev
                },
                data=json.dumps(new_user_doc)
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise ValueError(f"Failed to change password on CouchDB server: {exc}")

        print("Password changed successfully on CouchDB server")


    def change_password(self, args):
        """
        Change the CouchDB password in the configuration.
        """
        # if the password is not set, it will be prompted, do not echo it
        if args.new_password is None:
            new_password = getpass.getpass(
                f"enter the CouchDB password for the account "
                f"'{self.config['username']}' and database '{self.config['database']}': ")
        else:
            new_password = args.new_password

        # convert the password to bytes
        if isinstance(new_password, str):
            new_password = new_password.encode('utf-8')

        if 'encrypted_password' not in self.config:
            raise ValueError("No encrypted password found in the configuration.")

        # encrypt the new password
        encrypted_new_password = encrypt_password(new_password).decode()

        # show the old and new un-encrypted passwords
        old_password = decrypt_password(self.config['encrypted_password'])
        # DEBUG
        #print(f"old password: {old_password.decode('utf-8')}")
        #print(f"new password: {new_password.decode('utf-8')}")

        self.change_couchdb_password(
            uri=self.config['host_url'],
            username=self.config['username'],
            old_password=old_password,
            new_password=new_password
        )

        # save the updated configuration
        self.config['encrypted_password'] = encrypted_new_password
        self.write_config(self.config)
