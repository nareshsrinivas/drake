from logging.config import fileConfig

from alembic import context

from sqlalchemy import engine_from_config, pool

from dotenv import load_dotenv

import os

# -------------------------------------------------

# Load environment variables for Alembic

# -------------------------------------------------

load_dotenv()

# -------------------------------------------------

# Alembic Config

# -------------------------------------------------

config = context.config

fileConfig(config.config_file_name)

# -------------------------------------------------

# Import metadata

# -------------------------------------------------

from database import Base

from models import *  # noqa

target_metadata = Base.metadata

# -------------------------------------------------

# Get DATABASE_URL safely

# -------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set for Alembic")

# Convert async URL → sync URL for Alembic

SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)


# -------------------------------------------------

# Offline migrations

# -------------------------------------------------

def run_migrations_offline():
    context.configure(

        url=SYNC_DATABASE_URL,

        target_metadata=target_metadata,

        literal_binds=True,

        dialect_opts={"paramstyle": "named"},

    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------

# Online migrations (SYNC)

# -------------------------------------------------

def run_migrations_online():
    connectable = engine_from_config(

        config.get_section(config.config_ini_section),

        prefix="sqlalchemy.",

        poolclass=pool.NullPool,

    )

    with connectable.connect() as connection:
        context.configure(

            connection=connection,

            target_metadata=target_metadata,

        )

        with context.begin_transaction():
            context.run_migrations()


# -------------------------------------------------

# Entry point

# -------------------------------------------------

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()

