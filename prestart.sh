#!/bin/bash

# Let the DB start
export PYTHONPATH=".:${PYTHONPATH}"
python ./app/prestart.py
