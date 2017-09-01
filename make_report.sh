#!/bin/sh

python3 make_report_csv.py

echo "[$(date "+%Y-%m-%d %H:%M:%S")] Starting report web server ..."
python3 -m http.server