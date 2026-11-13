# Tavily power usage

Primary/backup discipline: `tavily-primary` first for every call; on connection/auth/timeout/quota/tool error call the same tool on `tavily-backup` exactly once. Empty results are NOT errors — refine the query on primary instead of failing over. Never call primary and backup in parallel for the same query.

Last resort: use the built-in `WebSearch` only after BOTH primary and backup have failed — state the error in one line, ask the user for permission and WAIT for approval. `WebFetch` needs no failover: use it directly on a known URL.

## Tool selection
| Need | Tool |
|---|---|
| Fresh info, docs, comparisons | `tavily_search` |
| Full content of known URLs | `tavily_extract` |
| Explore one site's structure | `tavily_map` |
| Read many pages of one site | `tavily_crawl` |
| Deep multi-step open question | `tavily_research` (expensive — only when a single search round is clearly insufficient) |

## Search patterns
- Multi-route: fire 2–4 differently-angled queries per topic (official docs / best practices / known issues / recent changes), then synthesize. Do not stop at one query.
- Use `search_depth: "advanced"` for technical topics; add `time_range` (e.g. "year") for fast-moving ecosystems; `include_domains` to pin official docs when noise is high.
- Prefer extract on the 2–3 best hits over trusting snippets. Snippets may be stale or truncated.
- Record findings in `docs/tdq/research/<slug>.md` as: query → source URL → distilled point. Cite sources in the spec.

## Cost control
- Search before crawl; crawl only when ≥3 pages of one site are needed.
- Cap: ~6 primary calls per analysis round; if still unclear, ask the user instead of burning more calls.
- Never echo API keys or auth headers into notes, logs, or prompts.

## Appendix

Layering: Tavily is the search tier for this workflow. Heavy research runs in a separate sub-agent so raw results stay out of the main conversation.
