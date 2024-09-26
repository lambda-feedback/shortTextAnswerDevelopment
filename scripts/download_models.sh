#!/bin/bash

set -e # Exit on error

# Check if MODEL_PATH is set
if [ -z "$MODEL_PATH" ]; then
    echo "MODEL_PATH is not set. Please set it to the path where model data should be downloaded."
    exit 1
fi

mkdir -p ${MODEL_PATH}

wget -O ${MODEL_PATH}/Phi-3.5-mini-instruct-Q6_K.gguf https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q6_K.gguf