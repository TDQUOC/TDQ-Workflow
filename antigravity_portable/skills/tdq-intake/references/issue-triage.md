# Handling an issue the user reported

Applies when the new request is a **bug report** rather than a feature: "it runs wrong",
"it hangs", "the result is not what I expected". The goal of triage is enough evidence to write a
fix spec — never a guess.

## The mandatory order

1. **Read the log first.** No proposed cause before you have looked at a log. Where logs
   live: the product's own log service, `docs/workinglog/<today>.md`, the latest test
   output, the previous session transcript in `~/.claude/projects/<project>/`.
2. **Reproduce.** Run the exact command the user ran. Cannot reproduce → ask the user for
   the command, input, version and environment before going any further.
3. **Capture when the bug is at the UI layer.** If computer use is needed to record the
   flow, save the capture into a temp folder **inside the repo**, with one note line giving
   the time and the reproduction steps. Delete the capture once the issue is closed.
4. **Frame the problem.** Write down: symptom · where it surfaces (file:line) · trigger
   condition · blast radius. Any box missing → back to step 1.
5. **Research the fix.** Search by the verbatim error and by library name + version. Rule
   for calling search: [tavily.md](../../tdq-conventions/references/tavily.md).
6. **Settle the evidence before writing the spec.** A fix spec must state the root cause,
   the fix, and a test that reproduces the bug (red before the fix).

## Common mistakes

| Wrong | Right |
|---|---|
| Fixing the symptom | Find the root cause, then fix |
| Fixed with no test | Write a test that reproduces the bug, red → green |
| Guessing the cause because there is no log | Turn detailed logging on, re-run, read the log |
| Deleting the capture/log at once | Keep it until the issue is closed, mention it in the report |
