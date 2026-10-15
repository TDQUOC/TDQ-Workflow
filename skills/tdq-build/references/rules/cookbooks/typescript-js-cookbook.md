# TypeScript & JavaScript Battle-Tested Cookbook
<!-- muc-luc-dong:
  When it applies=14-19 · What to do=20-21 ·
  Recipe 1: Safe Async Handling with Timeouts and AllSettled=22-53 ·
  Recipe 2: Typed Result Pattern (Avoid Untyped Throw)=54-80 ·
  Recipe 3: Immutable State Mutations=81-102 ·
  Recipe 4: Clean Dependency Injection via Interfaces=103-122 ·
  Recipe 5: Default-On Structured Logging=123-137 · Self-check=138
-->

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line -->.
Practical recipes for robust TypeScript/JS implementations: async handling, typed results, immutable mutations, dependency injection, and logging.

## When it applies

- Whenever you develop non-trivial TypeScript or JavaScript modules, backend endpoints, or CLI scripts.
- When an implementation faces unhandled promise rejections, silent async failures, untyped errors, or mutable state bugs.
- Load this file ONLY when resolving complex edge cases or structuring domain subsystems; do NOT preload into context for simple one-line changes.

## What to do

### Recipe 1: Safe Async Handling with Timeouts and AllSettled

Never allow a single failing promise to crash an entire batch silently:

```typescript
export async function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  let timer: NodeJS.Timeout;
  const timeoutPromise = new Promise<never>((_, reject) => {
    timer = setTimeout(() => reject(new Error(`Operation timed out after ${ms}ms`)), ms);
  });
  try {
    return await Promise.race([promise, timeoutPromise]);
  } finally {
    clearTimeout(timer!);
  }
}

export async function executeBatchSafe<T>(tasks: Promise<T>[]): Promise<{ successes: T[]; errors: Error[] }> {
  const results = await Promise.allSettled(tasks);
  const successes: T[] = [];
  const errors: Error[] = [];
  for (const res of results) {
    if (res.status === "fulfilled") {
      successes.push(res.value);
    } else {
      errors.push(res.reason instanceof Error ? res.reason : new Error(String(res.reason)));
    }
  }
  return { successes, errors };
}
```

### Recipe 2: Typed Result Pattern (Avoid Untyped Throw)

Encode expected failure modes into return types using a discriminated union:

```typescript
export type Result<T, E = Error> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export function ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

export function fail<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

export function parseJsonSafe<T>(raw: string): Result<T, Error> {
  try {
    const parsed = JSON.parse(raw) as T;
    return ok(parsed);
  } catch (err) {
    return fail(err instanceof Error ? err : new Error("Invalid JSON format"));
  }
}
```

### Recipe 3: Immutable State Mutations

Avoid in-place array or object mutation. Use spread operators or read-only arrays:

```typescript
export interface UserState {
  readonly id: string;
  readonly name: string;
  readonly tags: readonly string[];
}

export function addTag(user: UserState, newTag: string): UserState {
  if (user.tags.includes(newTag)) {
    return user;
  }
  return {
    ...user,
    tags: [...user.tags, newTag],
  };
}
```

### Recipe 4: Clean Dependency Injection via Interfaces

Decouple business logic from external I/O using typed interfaces:

```typescript
export interface StorageService {
  read(key: string): Promise<string | null>;
  write(key: string, data: string): Promise<void>;
}

export class ConfigManager {
  constructor(private readonly storage: StorageService) {}

  async loadSetting(key: string, defaultValue: string): Promise<string> {
    const raw = await this.storage.read(key);
    return raw ?? defaultValue;
  }
}
```

### Recipe 5: Default-On Structured Logging

All services must log structured information to stderr with ISO timestamps:

```typescript
export function logMessage(event: string, detail?: string, level: "INFO" | "WARN" | "ERROR" = "INFO"): void {
  if (process.env.TDQ_LOG === "0") {
    return;
  }
  const iso = new Date().toISOString();
  const line = detail ? `[${iso}] [${level}] ${event} — ${detail}` : `[${iso}] [${level}] ${event}`;
  process.stderr.write(`${line}\n`);
}
```

## Self-check

- [ ] All concurrent batches use allSettled or specify timeouts
- [ ] Known error conditions return a discriminated Result type instead of throw
- [ ] State manipulations return new immutable object copies
- [ ] I/O dependencies are decoupled via TypeScript interfaces
- [ ] Logging is active by default with ISO UTC timestamps and respects TDQ_LOG=0
