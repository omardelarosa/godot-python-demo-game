#!/bin/bash

# Source the python env
source $PROJECT_PATH/python/env.sh

# Synthesizes the pip install process locally with embedded python
exec $PYTHON_PATH -m pip "$@"