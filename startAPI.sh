#!/bin/bash
cd /home/umair/Desktop
source env/bin/activate
cd mawaqit-api
uvicorn main:app --host 0.0.0.0 --port 8000
