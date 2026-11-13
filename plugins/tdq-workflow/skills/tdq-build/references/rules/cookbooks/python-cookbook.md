# Python Battle-Tested Cookbook
<!-- muc-luc-dong:
  When it applies=13-18 · What to do=19-20 · Recipe 1: Safe Async Concurrency and Timeouts=21-43 ·
  Recipe 2: Atomic Transaction Context Manager=44-67 ·
  Recipe 3: Domain-Driven Error Hierarchy=68-95 ·
  Recipe 4: Clean Dependency Injection (Without Frameworks)=96-119 ·
  Recipe 5: Default-On Timestamped Logging=120-139 · Self-check=140
-->

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line -->.
Practical recipes for robust Python implementations: async concurrency, transactions, error handling, dependency injection, and logging.

## When it applies

- Whenever you build non-trivial Python services, workers, or CLI tools.
- When an implementation encounters async race conditions, unhandled exceptions, database transaction leaks, or complex dependency tangles.
- Load this file ONLY when debugging edge cases or designing complex subsystems; do NOT preload into context for simple one-line tasks.

## What to do

### Recipe 1: Safe Async Concurrency and Timeouts

Always shield critical background work, enforce timeouts, and avoid unhandled task cancellations:

```python
import asyncio
from typing import Sequence, TypeVar

T = TypeVar("T")

async def run_with_timeout(coro, timeout_seconds: float = 30.0):
    """Execute coroutine with strict timeout and clean cancellation."""
    try:
        async with asyncio.timeout(timeout_seconds):
            return await coro
    except TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout_seconds}s") from None

async def gather_safe(tasks: Sequence[asyncio.Task[T]]) -> list[T | Exception]:
    """Execute tasks concurrently, capturing exceptions without failing the batch."""
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### Recipe 2: Atomic Transaction Context Manager

Ensure all database operations commit together or roll back cleanly without connection leaks:

```python
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

@contextmanager
def transaction(connection: Any) -> Generator[Any, None, None]:
    """Atomic transaction scope: auto-commit on success, auto-rollback on error."""
    cursor = connection.cursor()
    try:
        cursor.execute("BEGIN;")
        yield cursor
        connection.commit()
    except Exception as exc:
        connection.rollback()
        raise RuntimeError(f"Transaction aborted: {exc}") from exc
    finally:
        cursor.close()
```

### Recipe 3: Domain-Driven Error Hierarchy

Never catch bare `Exception` silently. Group errors under a base domain exception:

```python
class DomainError(Exception):
    """Base exception for all domain-specific errors."""

class EntityNotFoundError(DomainError):
    def __init__(self, entity_type: str, entity_id: str):
        super().__init__(f"{entity_type} with ID '{entity_id}' not found.")
        self.entity_type = entity_type
        self.entity_id = entity_id

class ValidationError(DomainError):
    def __init__(self, field: str, message: str):
        super().__init__(f"Validation failed on {field}: {message}")
        self.field = field

def handle_safely(action):
    try:
        return action()
    except DomainError:
        raise
    except Exception as unexpected:
        raise DomainError(f"Unexpected operational failure: {unexpected}") from unexpected
```

### Recipe 4: Clean Dependency Injection (Without Frameworks)

Inject dependencies via constructors using Protocols (duck-typing interfaces):

```python
from typing import Protocol

class DataRepository(Protocol):
    def get_by_id(self, item_id: str) -> dict | None: ...
    def save(self, item: dict) -> None: ...

class OrderService:
    def __init__(self, repo: DataRepository) -> None:
        self._repo = repo

    def process_order(self, order_id: str) -> bool:
        order = self._repo.get_by_id(order_id)
        if not order:
            raise EntityNotFoundError("Order", order_id)
        order["status"] = "processed"
        self._repo.save(order)
        return True
```

### Recipe 5: Default-On Timestamped Logging

Every subsystem must emit structured, timestamped logs enabled by default:

```python
import os
import sys
from datetime import datetime, timezone

def log_event(event: str, detail: str = "", level: str = "INFO") -> None:
    """Default-on debug logging, switchable off via TDQ_LOG=0."""
    if os.environ.get("TDQ_LOG") == "0":
        return
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    msg = f"[{now}] [{level}] {event}"
    if detail:
        msg += f" — {detail}"
    print(msg, file=sys.stderr, flush=True)
```

## Self-check

- [ ] All async routines specify timeouts or safe task cancellation
- [ ] Database mutations run inside an explicit transaction context manager
- [ ] Exceptions inherit from a shared DomainError hierarchy and chain with `from err`
- [ ] Dependencies are injected via constructor arguments using Protocols
- [ ] Logging is active by default with ISO UTC timestamps and respects TDQ_LOG=0
