#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python notify_telegram.py
