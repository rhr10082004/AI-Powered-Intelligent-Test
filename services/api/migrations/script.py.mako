"""
Alembic initialization configuration.
"""

from alembic import config

# Get Alembic config
cfg = config.Config()

# Set sqlalchemy URL - will be overridden by env.py
cfg.set_main_option("sqlalchemy.url", "driver://user:pass@localhost/dbname")

# Setup script location
cfg.set_main_option("script_location", "services/api/migrations")

# Log file configuration
cfg.set_main_option("file_template", "%%(rev)s_%%(slug)s")
