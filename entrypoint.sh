#!/bin/bash
set -e

crond

case "$1" in
    develop)
        echo "Running Development Server"
        exec python main.py
        ;;
    test)
        echo "Test"
        exec python test.py
        ;;
    start)
        echo "Running Start"
        exec gunicorn -c gunicorn.py gladAnalysis:app
        ;;
    *)
        exec "$@"
esac
