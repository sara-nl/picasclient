
# First create configuration file with "python create_config.py"
# This will be stored in ~/.config/picas/conf.yml with password encrypted
# Here, the configuration is read and will be imported by the example scripts.
from picas.picas_config import PicasConfig
from picas.crypto import decrypt_password

config = PicasConfig(load=True)   
PICAS_HOST_URL = config.config['host_url']
PICAS_DATABASE = config.config['database']
PICAS_USERNAME = config.config['username']
PICAS_PASSWORD = decrypt_password(config.config['encrypted_password']).decode()

# Template for the "old" picasconfig.py, where configuration is stored as plain text
# PICAS_HOST_URL=""
# PICAS_DATABASE=""
# PICAS_USERNAME=""
# PICAS_PASSWORD=""
