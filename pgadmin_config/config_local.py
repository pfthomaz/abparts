# your-project-root/pgadmin_config/config_local.py

# This file is loaded by pgAdmin after config.py and config_distro.py.
# Any settings defined here will override defaults.

# Example: Change log file location to a specific path within the container's /var/lib/pgadmin volume
# This ensures logs persist with your pgadmin_data volume.
# Make sure the directory exists and pgAdmin user has permissions.
# import os
# DATA_DIR = '/var/lib/pgadmin' # This is the pgadmin_data volume mount point
# LOG_FILE = os.path.join(DATA_DIR, 'logs', 'pgadmin4.log')
# SQLITE_PATH = os.path.join(DATA_DIR, 'pgadmin4.db')
# SESSION_DB_PATH = os.path.join(DATA_DIR, 'sessions')
# STORAGE_DIR = os.path.join(DATA_DIR, 'storage')

# Example: If you wanted to disable the master password (NOT RECOMMENDED for production!)
MASTER_PASSWORD_REQUIRED = False

# Example: Adjust logging level for the console output
# import logging
# CONSOLE_LOG_LEVEL = logging.DEBUG # For more verbose logs

# You can add other configurations from pgAdmin's config.py reference here.
# Refer to pgAdmin documentation for available settings.