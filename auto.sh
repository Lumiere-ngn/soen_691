#!/bin/bash

# Setup/activatectivate conda
source setup_conda_env.sh
source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || \
source ~/miniconda3/etc/profile.d/conda.sh

conda activate open_interpreter_311

# Kill existing server
pkill -f "server/server.py"

# Start server
python3 server/server.py &
SERVER_PID=$!

sleep 2

# Start listener in background (IMPORTANT)
nc -l 4444 &
NC_PID=$!

# Run tests
python3 test_script_v3.py --commands "command_prompts.csv" --num_runs 1

# Cleanup
kill $SERVER_PID
kill $NC_PID