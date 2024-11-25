#!/bin/sh

until aerich upgrade
do
    echo "Waiting for db to be ready..."
    sleep 10
done
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000