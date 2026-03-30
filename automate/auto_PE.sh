#!/bin/bash
# Switch to demo_user
sudo -i -u demo_user

# Move into the test environment
cd ~/test_env

python3 test_script_v3.py --commands "command_prompts_PE.csv" --num_runs 1 --output "results_PE.csv"
