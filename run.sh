#!/bin/bash

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            shift
            TYPE=$1
            ;;
        --port)
            shift
            PORT=$1
            ;;
        *)
            ;;
    esac
    shift
done

if [ -z "$TYPE" ]; then
    TYPE="ws"
fi

if [ "$TYPE" = "ws" ]; then
    if [ -z "$PORT" ]; then
        PORT=""
    fi
    python -c "from ws import startapp; startapp('$PORT')"
elif [ "$TYPE" = "http" ]; then
    python -c "from api import startapp; startapp()"
elif [ "$TYPE" = "greeting" ]; then
    python -c "import greeting; greeting.main()"
elif [ "$TYPE" = "vector" ]; then
    python -c "from interact.llm.vector.script import main; main()"
fi
