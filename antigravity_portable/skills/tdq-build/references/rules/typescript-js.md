# TypeScript / JavaScript rules

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line -->. Load after `chung.md`; applies to
`.ts .tsx .js .jsx .mjs .cjs`.

## Sources

- typescript-eslint Shared Configs — https://typescript-eslint.io/users/configs (2026) —
  three config tiers: `recommended` (correctness bugs, use immediately) → `strict` → `stylistic`.
- typescript-eslint rule catalogue — https://typescript-eslint.io/rules — rules marked ✅
  belong to the recommended set: `no-explicit-any`, `no-floating-promises`, `await-thenable`,
  `ban-ts-comment`, `no-misused-promises`…
- Core JavaScript rules — https://eslint.org/docs/latest/rules (ESLint docs latest) —
  `no-unused-vars`, `no-shadow`, `no-redeclare`, `no-self-compare`…

## When it applies

- Writing or changing any TS/JS file, `.mjs/.cjs` config files and tests included.
- Before submitting: run the "Self-check" section; if the machine lacks `eslint`, write
  "not checked yet".

## The Intentionality rule

1. **`any` loses type intent**: `no-explicit-any` is in the recommended set — replace it with
   a concrete type, or with `unknown` narrowed step by step through type checks.
2. **A floating Promise swallows errors**: every Promise must be `await`ed, `return`ed, or
   deliberately marked as dropped (`no-floating-promises`, `no-misused-promises` and
   `await-thenable` are all ✅ recommended).
3. **Dead code and hidden type errors**: unused variables (`no-unused-vars`) → delete; a bare
   `@ts-ignore`/`@ts-expect-error` is blocked by `ban-ts-comment` — it must carry a reason.

## Measurable thresholds

- Cyclomatic ≤ 10, cognitive ≤ 15 per function — per `chung.md`. ESLint's `complexity` rule
  defaults to 20, so set it back to 10 in the config; never keep the default.
- Minimum config tier: `recommended` (core ESLint + typescript-eslint); a project moving up to
  `strict`/`stylistic` records that in the request's spec.

## What to do

1. Extend the right config tier: `eslint` recommended for JS plus `tseslint` recommended for
   TS; do not cherry-pick single rules before using the whole recommended set.
2. Declare types at the boundary (parameters and return values of exported functions); a bare
   `any` is banned.
3. Wherever an async function is called, that site decides explicitly: `await`, `return`, or a
   deliberate drop — calling and ignoring the result is banned.
4. Every `@ts-` directive must carry a reason right after the directive.
5. Run `eslint <path>` and fix every recommended-set error.

## Self-check

- [ ] `eslint` clean, or "not checked yet" recorded because the machine lacks eslint
- [ ] No bare `any`, no floating Promise, no `@ts-` without a description
- [ ] No unused variables/imports; exported functions typed at the boundary
- [ ] The 3 Intentionality questions in `chung.md` are answerable

## RIGHT/WRONG examples

```ts
// WRONG — bare any, floating promise, ts-ignore with no reason:
// @ts-ignore
function save(d: any) { fetch("/api", { body: d }); }
// RIGHT — types at the boundary, the promise is handled:
async function saveRecord(record: Record): Promise<void> {
  const res = await fetch("/api", { method: "POST", body: JSON.stringify(record) });
  if (!res.ok) throw new Error(`Save failed: HTTP ${res.status}`);
}
```
