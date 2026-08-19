# Images the user attached — how they enter the working log

Applies when a turn has attached images **and** that turn must write a working log (the repo
changed). Do this BEFORE calling `tdq_finish.py --log`.

## Steps

1. Source: the cache path `~/.claude/image-cache/<session-id>/<n>.<ext>`, already visible in
   the context of that same turn.
2. Target: `docs/workinglog/assets/<active_request hoặc "misc" nếu không có>/<n>.<ext>`.
   `n` = number of files already in the target folder + 1. **Never** reuse the index from the
   source cache — that number belongs to the session, not to the request.
3. Put `![<mô tả ngắn>](assets/<slug>/<n>.<ext>)` at the relevant spot inside the string
   passed to `--log`, next to the sentence describing that image. It need not lead the string.

## Rules

- Applies to **every** image the user attached in a repo-changing turn. Never judge "this one
  is probably irrelevant" and drop it.
- Images are **tracked in git** like any other file under `docs/workinglog/` — never gitignored.
- A failed copy (cache file gone) → tell the user, never skip it silently.
