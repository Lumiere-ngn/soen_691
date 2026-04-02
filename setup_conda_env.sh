#!/bin/bash

ENV_NAME="open_interpreter_311"

# Load conda
if [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
else
    echo "❌ Conda not found. Please install Miniconda or Anaconda."
    exit 1
fi

# Check if env exists
if conda env list | grep -q "$ENV_NAME"; then
    echo "✅ Environment already exists"
else
    echo "📦 Creating environment..."
    conda env create -f environment.yml
fi

echo "✅ Setup complete"
