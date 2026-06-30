#!/usr/bin/env bash
# Downloads the quantized GGUF model weight file for the ADTC 2026 submission.
# Idempotent: skips download if the file already exists.

set -euo pipefail

MODEL_DIR="model"
MODEL_FILE="qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

# Public Hugging Face URL for the quantized model.
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"

mkdir -p "${MODEL_DIR}"

if [ -f "${MODEL_PATH}" ]; then
  echo "Model already present at ${MODEL_PATH}, skipping download."
  exit 0
fi

echo "Downloading model to ${MODEL_PATH}..."
curl -L --fail --retry 3 -o "${MODEL_PATH}" "${MODEL_URL}"

echo "Download complete: ${MODEL_PATH}"
