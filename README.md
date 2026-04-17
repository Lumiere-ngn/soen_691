# Setup

## Environment 

These experiments are designed for a Linux system (native or WSL).

1. First, make sure you have a `.env` file with your `OLLAMA_API_KEY`, `OPENAI_API_KEY`, and any other model providers you may want to use (https://docs.openinterpreter.com/language-models/hosted-models/openai).

2. Second, ensure you have Anaconda or Miniconda installed on your machine.

3. Update `models.txt` to include the models you wish to use. They must be listed like <provider_name>/<model_name>.

The conda environment will automatically be setup when you run the main script `auto.sh`.

# Running Attack Experiments 

1. Inside `auto.sh`, ensure that the `--commands` argument is set to "command_prompts.csv".

2. Set the number of runs per model, per experiment, by setting the `--num_runs` argument. Default is 3. 

# Running Defense Experiments

## With attack scenarios 

1. Inside `auto.sh`, ensure that the `--commands` argument is set to "command_prompts.csv".

2. Set the number of runs per model, per experiment, by setting the `--num_runs` argument. Default is 1, since the outcome of the defense layer is deterministic. 

## With benign scenarios 

1. Inside `auto.sh`, ensure that the `--commands` argument is set to "command_prompts_safe.csv".

2. Set the number of runs per model, per experiment, by setting the `--num_runs` argument. Default is 1, since the outcome of the defense layer is deterministic. 

The agent output, per case ID, will all be saved in `automate/results` as CSV files. 