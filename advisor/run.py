#!/usr/bin/env python3
"""
ADTC 2026 — Nigerian Smallholder Agriculture Advisor
Offline inference script using llama.cpp + Igbo glossary RAG layer.
"""

import subprocess
import json
import os
import sys

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH  = os.path.join(BASE_DIR, "model", "qwen2.5-1.5b-instruct-q4_k_m.gguf")
LLAMA_CLI   = os.path.join(BASE_DIR, "llama.cpp", "build", "bin", "llama-cli")
PROMPT_FILE = os.path.join(BASE_DIR, "advisor", "system_prompt.txt")
GLOSSARY    = os.path.join(BASE_DIR, "advisor", "igbo_glossary.json")

# ── Load system prompt ──────────────────────────────────────────────────────
with open(PROMPT_FILE, "r") as f:
    SYSTEM_PROMPT = f.read().strip()

# ── Load Igbo glossary ──────────────────────────────────────────────────────
with open(GLOSSARY, "r") as f:
    glossary = json.load(f)

def build_glossary_hint(user_query: str) -> str:
    """Return relevant Igbo terms if the query mentions known crops or concepts."""
    query_lower = user_query.lower()
    matches = []
    for category, terms in glossary.items():
        for english, igbo in terms.items():
            if english in query_lower:
                matches.append(f"{english} ({igbo})")
    if not matches:
        return ""
    return "\n[Igbo terms: " + ", ".join(matches[:6]) + "]"

def ask(user_query: str, max_tokens: int = 300) -> str:
    """Run inference and return the model's response."""
    glossary_hint = build_glossary_hint(user_query)
    augmented_query = user_query + glossary_hint

    full_prompt = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{augmented_query}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    cmd = [
        LLAMA_CLI,
        "-m", MODEL_PATH,
        "--prompt", full_prompt,
        "-n", str(max_tokens),
        "-t", "4",
        "-c", "1024",
        "-ngl", "0",
        "--temp", "0.7",
        "--repeat-penalty", "1.1",
        "--log-disable",
    ]

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    output = ""
    for char in iter(lambda: proc.stdout.read(1), ""):
        output += char
        if "<|im_end|>" in output:
            break
        # Stop at natural sentence end after enough tokens
        if len(output) > 100 and output.rstrip().endswith((".", "!", "?")):
            last_nl = output.rfind("\n")
            if last_nl > 80:
                break

    proc.terminate()
    proc.wait()

    # Clean up any trailing tokens or prompt leakage
    response = output.replace("<|im_end|>", "").strip()
    return response


# ── CLI entry point ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🌾 Nigerian Agriculture Advisor (offline)")
    print("   Type your question in English or Pidgin. Ctrl+C to exit.\n")

    if len(sys.argv) > 1:
        # Single query mode: python run.py "my cassava is dying"
        query = " ".join(sys.argv[1:])
        print(f"Q: {query}\n")
        print(ask(query))
    else:
        # Interactive mode
        while True:
            try:
                query = input("You: ").strip()
                if not query:
                    continue
                print("\nAdvisor:", ask(query), "\n")
            except KeyboardInterrupt:
                print("\nGoodbye.")
                break