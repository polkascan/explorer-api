import sys, os
sys.path = ['', '..'] + sys.path[1:]

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from dotenv import load_dotenv

from app.db import BaseModel
from app import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

from app.models.runtime import *
from app.models.explorer import *
from app.models.harvester import *

target_metadata = BaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env_file = ".env"
if os.path.exists(".local.env"):
    env_file = ".local.env"

load_dotenv(os.path.join(BASE_DIR, "..", env_file))
sys.path.append(BASE_DIR)

DB_CONNECTION = os.environ['API_SQLA_URI']
DEBUG = True


def include_object(object, name, type_, reflected, compare_to):
    if type_ == 'table' and object.schema == settings.DB_HARVESTER_NAME:
        return False

    return True


def render_item(type_, obj, autogen_context):
    """Apply custom rendering for selected items."""

    if type_ == 'type' and isinstance(obj, HashBinary):
        default_name = "%r" % obj
        return default_name.replace("HashBinary", "sa.BINARY")
    elif type_ == 'type' and isinstance(obj, HashVarBinary):
        default_name = "%r" % obj
        return default_name.replace("HashVarBinary", "sa.VARBINARY")

    # default rendering for other objects
    return False


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    db_config = {
        'sqlalchemy.url': DB_CONNECTION,
        'sqlalchemy.echo': DEBUG
    }

    connectable = engine_from_config(
        db_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()