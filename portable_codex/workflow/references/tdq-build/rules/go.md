# Go rules

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line -->. Load after `chung.md`; applies to every `.go` file.

## Sources

- Effective Go — https://go.dev/doc/effective_go — MixedCaps naming, gofmt, doc comments.
- Google Go Style Guide — https://google.github.io/styleguide/go — additional style standards.
- GDS Way Go — https://gds-way.digital.cabinet-office.gov.uk/manuals/programming-languages/go.html —
  recommends `golangci-lint` as the meta-linter (bundling `staticcheck`, `errcheck`, `gosec`,
  `revive`; `golint` is deprecated) with `go vet` running in CI.
- Uber Go Style Guide — https://github.com/uber-go/guide/blob/master/style.md — the minimum
  linter set: errcheck, goimports, revive, govet, staticcheck.

## When it applies

- Writing or changing any `.go` file, `_test.go` included.
- Before submitting: run the "Self-check" section; if `golangci-lint` is missing try
  `go vet ./...`, and if both are missing write "not checked yet".

## The Intentionality rule

1. **Off-standard names**: Go uses `MixedCaps`/`mixedCaps`, never underscores; an exported
   identifier is capitalised and must carry a doc comment starting with that very name.
2. **Swallowing errors**: ignoring `err` is the gravest Go defect — `errcheck` catches every
   call returning an error that goes unchecked; a genuine drop is written `_ = f()` with a
   comment giving the reason.
3. **Dead code**: the Go compiler already blocks unused imports and locals; the rest
   (uncalled functions, unreachable branches) is reported by `staticcheck` → delete.

## Measurable thresholds

- Cyclomatic ≤ 10, cognitive ≤ 15 per function — per `chung.md`; `gocyclo` has no shared
  default, so take TDQ's level of 10 directly and do not pick another.
- The minimum linter set that must be enabled: errcheck, govet, staticcheck (per the Uber Go
  Style Guide).

## What to do

1. Format with `gofmt`/`goimports` before submitting — unformatted code counts as unfinished.
2. Check `err` IMMEDIATELY after the call returning it; when passing an error up, wrap it with
   context saying which operation failed.
3. Every exported identifier carries a doc comment starting with its name (`// SumOf adds…`).
4. Keep interfaces small, accepting interfaces and returning structs where that matches the
   repo's existing code.
5. Run `golangci-lint run <path>` (fallback: `go vet ./...`) and fix everything reported.

## Self-check

- [ ] `golangci-lint run` or `go vet` clean, or "not checked yet" recorded
- [ ] No call drops `err` without a reason comment
- [ ] The code went through `gofmt`; exported identifiers carry correctly shaped doc comments
- [ ] The 3 Intentionality questions in `chung.md` are answerable

## RIGHT/WRONG examples

```go
// WRONG — err dropped, name carries an underscore:
func read_cfg(p string) []byte {
    b, _ := os.ReadFile(p)
    return b
}
// RIGHT — err is checked and carries context:
// ReadConfig reads the config file at path.
func ReadConfig(path string) ([]byte, error) {
    b, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("read config %s: %w", path, err)
    }
    return b, nil
}
```
