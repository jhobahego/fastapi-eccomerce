from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Agregar el path de la aplicación para que Alembic encuentre los modelos
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base
from app.config import settings

# Importación de modelos aquí para que Base los conozca
from app.models.user import User  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.cart import Cart, CartItem  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Establece la URL de la base de datos desde tu configuración central
if settings.DATABASE_URL:
    config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
    print(f"Alembic is using database URL: {settings.DATABASE_URL}")
else:
    raise Exception("DATABASE_URL is not set in the environment variables")


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
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
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get the configuration section and ensure it exists to satisfy the type checker.
    configuration = config.get_section(config.config_ini_section)
    if not configuration:
        raise Exception(
            f"Alembic config section '{config.config_ini_section}' not found."
        )

    # Get the database URL from the central config and add it to the
    # dictionary for SQLAlchemy's engine_from_config.
    db_url = config.get_main_option("sqlalchemy.url")
    if db_url:
        configuration["sqlalchemy.url"] = db_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
