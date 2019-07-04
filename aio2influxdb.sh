#!/bin/bash
cd "$(dirname "$0")"
. _venv/bin/activate
python aio2influxdb.py
