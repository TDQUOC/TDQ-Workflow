# Community 112

> 7 nodes · cohesion 0.33

## Key Concepts

- **turn_log_clear()** (6 connections) — `scripts/tdq_state.py`
- **turn_log_read()** (5 connections) — `scripts/tdq_state.py`
- **_atomic_write()** (4 connections) — `scripts/tdq_state.py`
- **turn_log_path()** (4 connections) — `scripts/tdq_state.py`
- **_row_age_ok()** (3 connections) — `scripts/tdq_state.py`
- **Events of the current session, skipping rows older than 6 hours (RR12).** (1 connections) — `scripts/tdq_state.py`
- **Drop this session's rows (at turn start). Other sessions' rows are kept.** (1 connections) — `scripts/tdq_state.py`

## Relationships

- [Community 0](Community_0.md) (6 shared connections)
- [Community 13](Community_13.md) (2 shared connections)
- [Community 3](Community_3.md) (2 shared connections)

## Source Files

- `scripts/tdq_state.py`

## Audit Trail

- EXTRACTED: 15 (88%)
- INFERRED: 2 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*