#!/usr/bin/env bash

root=$1
source $root/venv/bin/activate

pip install -r $root/requirements.txt
