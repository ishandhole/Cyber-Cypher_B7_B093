#!/bin/bash

# Configuration
VENV_BIN=".venv/bin"
PYTHON="$VENV_BIN/python"
STREAMLIT="$VENV_BIN/streamlit"
PID_FILE=".server_pids"
LOG_DIR="logs"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

mkdir -p $LOG_DIR

function start {
    if [ -f "$PID_FILE" ]; then
        echo -e "${RED}Servers seem to be running (PID file exists). Run './manage.sh stop' first.${NC}"
        exit 1
    fi

    echo -e "${GREEN}Starting API Server...${NC}"
    nohup $PYTHON main.py > "$LOG_DIR/api.log" 2>&1 &
    API_PID=$!
    echo "API PID: $API_PID"

    echo -e "${GREEN}Starting Dashboard...${NC}"
    nohup $STREAMLIT run ui/dashboard.py > "$LOG_DIR/ui.log" 2>&1 &
    UI_PID=$!
    echo "Dashboard PID: $UI_PID"

    echo "$API_PID" > $PID_FILE
    echo "$UI_PID" >> $PID_FILE

    echo -e "${GREEN}Servers are running!${NC}"
    echo "API: http://localhost:8000"
    echo "Dashboard: http://localhost:8501"
    echo "Logs are in $LOG_DIR/"
}

function stop {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${RED}No PID file found. Are servers running?${NC}"
        # Fallback: aggressive kill if user wants
        pkill -f "main.py"
        pkill -f "streamlit run ui/dashboard.py"
        exit 0
    fi

    echo -e "${GREEN}Stopping servers...${NC}"
    while read pid; do
        if ps -p $pid > /dev/null; then
            kill $pid
            echo "Killed PID $pid"
        else
            echo "PID $pid not found"
        fi
    done < $PID_FILE

    rm $PID_FILE
    echo -e "${GREEN}Servers stopped.${NC}"
}

function status {
    if [ -f "$PID_FILE" ]; then
        echo -e "${GREEN}Servers are RUNNING.${NC}"
        cat $PID_FILE
    else
        echo -e "${RED}Servers are STOPPED.${NC}"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: ./manage.sh {start|stop|restart|status}"
        exit 1
        ;;
esac
