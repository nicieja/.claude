# Refactor guide

The reference `code-refactor` loads every run. It lists the marks that iteration leaves in code and the order that slices run in, plus the recipe for the baseline harness and the template of the plan file. Tune it after each refactor, because it is the spec.

## What iteration leaves behind

Code that reached its form through experiments and changed requirements still shows the path it took. Each mark below comes with the change that removes it. A mark is a lead for the survey, and it becomes a slice only after the survey finds it in the code.

- **Dead code.** A function whose only caller is its own test, or an export that other files never import. Delete it, and point the test at the code that is still in use. The props and options that a callee ignores go too.
- **Scattered file access.** Paths and readers spread across scripts, or a script that imports another script for a path or a helper. Move the paths and the readers into one module, next to one writer.
- **Writers that format in different ways.** One writer of a kind of file formats its output and another does not, and a rerun of an untouched generator then changes a committed file. One writer fixes it, and the first rerun after the change commits the format once.
- **A file format in pieces.** The check of a file is in one module and its writer in another. One module per format gets the check and the reader, and also the writer and the formatter.
- **Imports in the wrong direction.** A builder imports its consumer to compute a value that only the consumer reads. The consumer computes the value, and the generated file loses the field.
- **One call sequence in every caller.** Each caller wraps the engine in the same lines of code. One entry point replaces them. It takes one request object with the defaults in one place, and positional arguments become fields of that object.
- **Many names for one concept.** A limit has one name in the core and another in the UI. Pick one name for the code. The flags and messages that users see keep their names.
- **Many tables for one set of values.** The same values are keyed in a different way in several files. One table replaces them, and each old table becomes a field of it.
- **Long functions with many jobs.** Split them into named steps, and move each comment next to the rule that it explains.
- **Repeats in markup and in tests.** The same markup repeats across layouts, or a lookup or a fixture repeats across tests. A component or a test helper replaces the repeats.
- **Unread data.** A generated file, or a file that users download, has fields that its readers ignore. The writer drops them. Measure the size before and after, compressed as well as raw.
- **Hand-written grouping.** A loop builds a map of lists where the runtime has a built-in, such as `Map.groupBy` or Ruby's `group_by`. Use the built-in only where each item goes under one key. A loop that files one item under many keys keeps its loop.
- **Stale comments.** A comment explains a requirement that is gone. Rewrite it for the current rule, or delete it.

A cleanup that changes an output is outside this list, however small it is. It goes to the findings for later.

## Slice order

Order the slices so that each one works on code in its final place.

1. **Baseline.** This is always slice 0.
2. **Dead code.** It goes first, because each later move then has less code to move.
3. **Modules and file formats.** A function moves to its final module before a slice splits it.
4. **Function splits and one entry point.**
5. **Shared names and tables**, after the modules that they touch exist.
6. **UI slices**, each with its manual look, and then the **test helpers**, after the moves that change the tests.
7. **Output changes**, such as fields that a generated file drops. They come late and one per slice, because only these slices expect a diff.
8. **Second look**, and then the **docs** slice last.

New slices from the second look go before the docs slice, and their numbers continue from the highest number in the plan. A slice that splits gets a letter, such as 2b, and goes right after its parent. The run order is the order in the file, and the numbers only identify the slices.

## The baseline harness

The harness pins every output of the code in scope before slice 1. After each slice, a diff against it decides whether the behavior is the same.

It is in a git-ignored directory inside the repo, such as `.claude/<slug>/`. The directory has `check.sh` and a probe script, plus the saved baseline and a log file. A new session can read it there, and `git check-ignore <path>` confirms that git ignores it. The plan gives the directory, and it tells how to rebuild the baseline if the directory is lost. The rebuild checks out the slice 0 commit in a `git worktree` and saves the outputs there.

### What to pin, strongest first

1. **Generated files in the repo.** Regenerate them, then run `git diff --exit-code <path>`. The comparison is byte for byte, and the key order of a serialized object is part of the output.
2. **Script output.** Save the stdout of each script in scope and diff against it. Send stderr elsewhere.
3. **A probe.** This is a short script that calls the entry point with the fewest tests, such as the path that the UI or an API client takes. Use real inputs, such as the case in a bug report, at two or more settings of each option. The probe prints what the consumers read. It also prints a hash of the intermediate artifact that the core consumes, such as a SQL string or a request body. The hash is stricter than the result, because two different inputs can give the same result.
4. **The suite and the linter.** They run last.

### Rules for the harness

- **Stable values only.** Timings and dates go to stderr or to a file of their own. The log records the timings of slice 0, and the check leaves them out of the comparison.
- **Domain values.** Print the values that a user would recognize, such as the members of a set in sorted order. Leave out internal ids, because a slice can remove them.
- **Stop at the first failure.** The script uses `set -e` and runs one step after another. Long logs, such as the test output, go to a file, and the check shows the tail of that file on failure.
- **Network steps once.** A step that downloads data runs once, in the slice that touches it, and the tree must be unchanged after it. The check of each slice runs offline.
- **Manual checks by slice.** A look at a page in a browser runs only for the slices that the plan lists. When a look is incomplete, such as a window that does not resize, the log says what was checked in its place.
- **Drift before slice 1.** Run each generator on the unchanged code before slice 1. A diff at that point is drift from before the refactor. It is a precondition or a slice of its own, and never noise to ignore.

### The mutation test

A check is trusted only after it fails once. In slice 0, change one constant in the core on purpose, such as a tiebreak weight or a rounding step, and run the check. It must fail at the step that should see the change. After the revert, it must pass again. The log records both runs.

### Planned output changes

The plan states each planned output change before its slice runs. An example is "the generated file loses the `total` field". The check then applies exactly that change to the baseline and compares. Strip the field from the old file, and the old and new files must be equal. After the slice, save the new output as the baseline and write the change in the log.

## Plan template

Write the plan in the plans directory that Step 0 found, as `<area>-refactor.md`, from this skeleton. Replace the parts in angle brackets, and delete a rule that does not apply.

```markdown
# Refactor <the code in scope>

## Context

<How the code got to its current state. The requirements that changed, and the marks that the survey found, each with a file.>

The goal is the same behavior in less code, with each concept in one module. This file is the checklist. Each slice has a box, and each box gets a log line when it is done.

## Rules for every slice

- **Behavior stays the same.** The checks compare every output with the baseline from slice 0. A slice that must change an output says which output, and the check then expects exactly that change.
- **Each slice ends in its own commit**, after the checks pass. Tick the box and add a log line with the date. The line also records what the slice found or deferred.
- **Tests change only when the code under test moves or gets a new name.** A test that moves keeps its notes.
- **No defensive code.** Validate at the boundary (<the inputs from outside>) and trust the data inside. A bad input crashes with a clear message. Keep the crashes that exist.
- **Behavior changes go to "Findings for later".** A slice that finds a bug writes it down and does not fix it.
- <A rule of this project, such as "The key order in <file> is part of the output.">

## The checks

Slice 0 writes the check script at `<ignored dir>/check.sh`. <How to rebuild the baseline if the directory is lost.>

The script runs these steps one after another and stops at the first failure.

1. <Regenerate the files, then run `git diff --exit-code <path>`.>
2. <The script output, compared with `baseline/<name>.txt`.>
3. <The probe, compared with `baseline/probe.txt`. Its inputs, and what it prints.>
4. <The test suite and the linter.>

<The slices that need a manual check, and the check. The step that needs the network, and its slice.>

## Slices

### - [ ] Slice 0. A green baseline

- <Each precondition to fix, in its own commit.>
- Write the probe and `check.sh`, and save the baseline outputs.
- Mutation-test the check. Change <a constant in the core> on purpose, and the check must fail. Revert the change.
- Record the timings of the probe. Timing is not a check.

### - [ ] Slice 1. <Title>

<What moves where, and why. The output change, if the slice has one, and how the check expects it.>

### - [ ] Slice <N>. A second look

Ask the `code-simplifier` agent for one pass over the code after the slices above. Its findings become new slices before the docs slice, or findings for later.

### - [ ] Slice <N+1>. Docs (last)

- <The docs that point to moved code.>
- Move this file to <the place for finished plans>.

## Findings for later

These change behavior, and they wait until the refactor is done. Each one says what shows it, such as a failing test or a reproduction, or that it was found by reading.

## Log

Add one line per slice with the date and a short note. `git log -- <this file>` lists the commit of each slice.
```

A log line reads `- YYYY-MM-DD, slice N. <What the slice found or deferred, and any measurement.>` It leaves out the hash of its own commit, because the plan is part of that commit. Every slice commit changes the plan, and `git log -- <plan>` lists them. The line of slice 0 gives the hash of the commit that the baseline comes from.
