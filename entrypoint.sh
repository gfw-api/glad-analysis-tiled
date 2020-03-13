#!/bin/bash
set -e

case "$1" in
    develop)
        echo "Running Development Server"
        exec python main.py
        ;;
    test)
        echo "Test"
        exec python -m unittest -v gladAnalysis.tests
        ;;
    start)
        echo "Running Start"
        exec gunicorn -c gunicorn.py gladAnalysis:app
        ;;
    *)
        exec "$@"
esac
