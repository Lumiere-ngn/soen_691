source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || \
source ~/miniconda3/etc/profile.d/conda.sh
conda activate open_interpreter_311
pkill -f "../server/server.py"
python3 ../server/server.py &
SERVER_PID=$!
sleep 2
python3 test_script_v3.py --commands "command_prompts.csv" --num_runs 1
kill $SERVER_PID