# Technical Report — Nigerian Smallholder Agriculture Advisor

**Team ID:** your-team-id
**Domain:** agriculture
**Model:** Qwen2.5-1.5B-Instruct-Q4_K_M

---

## Problem

Nigeria has an estimated 70+ million people working in agriculture, the overwhelming majority of them smallholder farmers without reliable internet access, stable electricity, or the budget for cloud-based advisory tools. When a farmer in Imo, Enugu, or Kaduna State notices yellowing cassava leaves or wants to know the right planting window for maize, the practical options are a long trip to an extension officer, guesswork, or asking a neighbor — none of which scale and none of which work at 6am in a field with no signal.

This submission is an offline, on-device agriculture advisory assistant that runs entirely on an 8GB consumer laptop with no GPU and no internet connection. The target user is a Nigerian smallholder farmer, an agricultural extension worker serving multiple communities, or a cooperative officer who needs fast, accurate crop, livestock, and market guidance without depending on connectivity that may not exist where they work.

The assistant communicates in plain English and Nigerian Pidgin — the two languages most consistently understood across Nigeria's linguistic diversity — supported by a curated Igbo glossary layer for core farming terminology, so users can navigate and recognize key terms in their own language even where full generative fluency in Igbo is not yet achievable on a model this size.

---

## Design Decisions

- **Base model:** Qwen2.5-1.5B-Instruct, chosen over larger models (7B-class) and smaller models (0.5B) as a deliberate middle ground. At 1.5B parameters, the model retains enough instruction-following and reasoning capacity for multi-step agricultural advice (diagnose → explain → recommend) while staying comfortably within the 7GB RAM ceiling with significant headroom for the RAG retrieval layer running alongside it.
- **Quantization:** GGUF Q4_K_M. This level keeps perplexity degradation modest relative to fp16 while reducing the on-disk and in-memory footprint to roughly 1GB, well under budget.
- **Language strategy — the honest tradeoff:** We surveyed available small (under 3B), GGUF-compatible, llama.cpp-ready models for genuine Igbo generative fluency. None exist. The closest candidate, N-ATLaS-LLM (Nigeria's government-backed Llama-3-8B fine-tune on Yoruba/Hausa/Igbo), is too large to fit this hardware profile at competitive speed and efficiency, and independent benchmarking (AfroBench) shows it still only reaching roughly 24.6% accuracy on Igbo tasks even after fine-tuning. Rather than ship a 1.5B model improvising broken Igbo — which would actively mislead a farmer making a planting decision — we chose to be explicit about this constraint: the conversational layer runs in English and Nigerian Pidgin, both of which the base model handles with reasonable fluency, while a structured Igbo glossary (crop names, common symptoms, weather/seasonal terms) is surfaced through the RAG retrieval layer to keep the experience locally grounded without fabricating fluency the model doesn't have.
- **Alternatives considered and rejected:**
  - *N-ATLaS-LLM (8B, Yoruba/Hausa/Igbo fine-tune)* — genuine African language training data, but its memory footprint at any reasonable quantization leaves little room for the RAG layer and risks both the Speed and Efficiency scores. Rejected for this hardware profile.
  - *General multilingual models with broad language claims (Phi-3, base Qwen2.5 without scoping)* — Qwen2.5's official multilingual support list does not include Igbo, Yoruba, Hausa, or Nigerian Pidgin at all; defaulting into unscoped multilingual claims would have been dishonest.
  - *Q8_0 / fp16 quantization* — better quality but roughly 2-4x the memory footprint for marginal accuracy gains on this domain; not worth the Efficiency score penalty.
  - *Q2_K quantization* — too aggressive; produced noticeably degraded reasoning on multi-step agricultural diagnosis prompts during testing.

---

## Constraints

- **Target hardware:** 8GB RAM, integrated graphics only, Ubuntu 22.04 — pure CPU inference via llama.cpp, no GPU acceleration available or assumed.
- **Connectivity:** Zero internet dependency at inference time. All retrieval is local (on-disk RAG corpus), not API-based.
- **Development hardware constraint:** The development machine (2014 MacBook Air, 4GB RAM) is below the target profile and cannot run the model directly. All benchmarking and profiling was performed on Google Colab to approximate target-hardware conditions before submission; final scoring numbers come from the official ADTC audit on the standard laptop profile.
- **Data availability:** Nigerian agriculture data on crop diseases, planting calendars, and pest identification is fragmented across extension service PDFs and research papers rather than a single clean dataset; the RAG corpus was manually curated and structured rather than scraped in bulk, to ensure factual reliability over coverage breadth.
- **Language constraint:** No existing small open-source generative model has genuine Igbo fluency; this shaped the decision to scope language claims to what can be honestly delivered (see Design Decisions).

---

## Benchmarks

| Metric | Value |
|---|---|
| Machine | Google Colab (CPU runtime, approximating target profile) |
| RAM at peak | *(fill in after profiler run)* |
| Time to first token | *(fill in after profiler run)* |
| Generation speed | *(fill in after profiler run)* |
| Thermal throttling | N/A on cloud runtime — verified via official ADTC audit |

These are self-reported development benchmarks gathered via the `adtc-profiler` tool in participant mode. Official scores are measured by the ADTC profiler on the standard evaluation machine during Gate 2.

---

## Cross-Disciplinary Integration

This submission pairs the local LLM with a structured agricultural knowledge retrieval layer (RAG) over curated Nigerian crop, pest, and market data, plus a localized language glossary. The pairing is load-bearing, not cosmetic: removing the RAG layer would mean the model falls back on generic, non-Nigeria-specific agricultural knowledge from its pretraining, losing the local crop varieties, regional pest pressures, and market terminology that make the tool actually useful to its target user.
