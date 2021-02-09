#!/bin/sh

# Let the DB start
export PYTHONPATH=".:${PYTHONPATH}"
python ./app/prestart.py
# Run migrations
#alembic upgrade head
