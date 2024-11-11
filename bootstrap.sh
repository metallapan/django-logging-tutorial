#!/usr/bin/sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/inv init run
