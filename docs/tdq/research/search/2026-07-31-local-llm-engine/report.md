# Deep search report — 2026-07-31-local-llm-engine

- Agent: 5 · finding sau dedup: 34 · route hỏng: 0

| # | Claim | Nguồn | Route xác nhận | Score |
|---|---|---|---|---|
| 1 | Ollama hỗ trợ Structured Outputs bằng cách giới hạn output của model theo JSON s | https://ollama.com/blog/structured-outputs | tổng quát: LLM local tham số thấp (3B–14B) làm engine code-agent — runtime (1) | 10 |
| 2 | Dòng model open-weights Qwen2.5-Coder được huấn luyện trên 5.5 trillion token nh | https://qwenlm.github.io/blog/qwen2.5-coder/ | tổng quát: LLM local tham số thấp (3B–14B) làm engine code-agent — runtime (1) | 10 |
| 3 | llama.cpp sử dụng GBNF (GGML BNF) grammars để định hình và bắt buộc output của m | https://raw.githubusercontent.com/ggerganov/llama.cpp/master/grammars/README.md | tổng quát: LLM local tham số thấp (3B–14B) làm engine code-agent — runtime, constrained decoding stack local macOS — mlx-lm / llama.cpp GBNF / XGrammar-2 / Ollama-MLX schema (1) | 10 |
| 4 | DeepSeek-R1-Distill-Qwen-14B được fine-tune từ base model Qwen2.5-14B bằng cách  | https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B | model (1) | 10 |
| 5 | Họ Qwen2.5-Coder cung cấp 6 quy mô kích thước mô hình bao gồm 0.5B, 1.5B, 3B, 7B | https://qwenlm.github.io/blog/qwen2.5-coder-family/ | model (1) | 10 |
| 6 | Outlines đảm bảo sinh đầu ra có cấu trúc (structured outputs) trực tiếp trong qu | https://github.com/dottxt-ai/outlines | kỹ thuật harden (1) | 10 |
| 7 | GBNF (GGML BNF) là định dạng formal grammar được tích hợp trong llama.cpp để ép  | https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md | kỹ thuật harden (1) | 10 |
| 8 | Instructor sử dụng Pydantic để thực hiện validation, đảm bảo type safety và sinh | https://github.com/jxnl/instructor | kỹ thuật harden (1) | 10 |
| 9 | XGrammar (với phiên bản XGrammar-2 phát hành 05/2026) hỗ trợ sinh dữ liệu có cấu | https://github.com/mlc-ai/xgrammar | kỹ thuật harden, constrained decoding stack local macOS — mlx-lm / llama.cpp GBNF / XGrammar-2 / Ollama-MLX schema (1) | 10 |
| 10 | Mô hình 4B tham số được huấn luyện bằng EGPO (FunRL) đạt state-of-the-art trên B | https://arxiv.org/abs/2508.05118 | đo sâu Qwen3 8B/14B và Phi-4 tool-calling ≤14B — BFCL / multi-turn / quantization Q4 (1) | 10 |

(Chỉ hiện top 10/34 — đủ trong merged.json)

Sinh lúc: 2026-07-31T18:09:02+07:00 · rank tất định bằng code (route xác nhận → URL sống → có quote → score → thứ tự route).
