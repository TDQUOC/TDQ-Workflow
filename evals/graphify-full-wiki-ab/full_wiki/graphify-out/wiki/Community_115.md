# Community 115

> 6 nodes · cohesion 0.40

## Key Concepts

- **turn_log_clear()** (6 connections) — `scripts/tdq_state.py`
- **turn_log_read()** (5 connections) — `scripts/tdq_state.py`
- **turn_log_path()** (4 connections) — `scripts/tdq_state.py`
- **_row_age_ok()** (3 connections) — `scripts/tdq_state.py`
- **Events of the current session, skipping rows older than 6 hours (RR12).** (1 connections) — `scripts/tdq_state.py`
- **Drop this session's rows (at turn start). Other sessions' rows are kept.** (1 connections) — `scripts/tdq_state.py`

## Relationships

- [Community 0](Community_0.md) (5 shared connections)
- [Community 7](Community_7.md) (2 shared connections)
- [Community 4](Community_4.md) (1 shared connections)

## Source Files

- `scripts/tdq_state.py`

## Audit Trail

- EXTRACTED: 12 (86%)
- INFERRED: 2 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*