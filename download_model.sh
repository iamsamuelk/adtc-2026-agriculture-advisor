#!/usr/bin/env bash
# Downloads the quantized GGUF model weight file for the ADTC 2026 submission.
# Idempotent: skips download if the file already exists.

set -euo pipefail

# Anchor to this script's own directory so it works no matter what
# directory the sandbox/orchestrator invokes it from.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$HERE/model"
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
# Download to a .partial file first, then move into place atomically.
# If curl dies mid-download, no corrupted file is left at MODEL_PATH,
# so the idempotency check above can't be fooled into "skipping" a broken file.
curl -L --fail --retry 3 --http1.1 -C - -o "${MODEL_PATH}.partial" "${MODEL_URL}"
mv "${MODEL_PATH}.partial" "${MODEL_PATH}"

echo "Download complete: ${MODEL_PATH}"
