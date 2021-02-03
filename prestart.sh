#!/bin/sh

# Let the DB start
python ./app/prestart.py
# Run migrations
alembic upgrade head
