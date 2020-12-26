#!/bin/bash

# Source the python env
source $PROJECT_PATH/python/env.sh

exec $PYTHON_PATH "$@"