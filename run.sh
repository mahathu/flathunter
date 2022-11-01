#!/bin/bash

if ! pkill -f auto_apply; then
    source .venv/bin/activate
    nohup python3.9 auto_apply.py &
else
    echo "Script was already running and has been killed"
fi
