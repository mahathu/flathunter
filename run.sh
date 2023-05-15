#!/bin/bash

if ! pkill -f main; then # probably this should be urgently changed
    source .venv/bin/activate
    nohup python3 main.py &
else
    echo "Script was already running and has been killed"
fi
