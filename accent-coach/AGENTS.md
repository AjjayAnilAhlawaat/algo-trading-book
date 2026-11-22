# AGENTS.md — rules for every coding agent (human or AI)

Read `.specify/memory/constitution.md` first. If a task conflicts with it, stop and ask.

## Workflow (Spec-Anchored Development)

1. **Never code without a spec.** Work only on tasks listed in `specs/NNN-*/tasks.md`.
2. **One task = one vertical slice = one commit.** Tick the checkbox in `tasks.md` in the same commit.
3. **Test first.** Write the failing test named after the EARS ID (e.g. `test_e001_03_...`) before the implementation.
4. **Run the task's verify command** (listed beside each task) and paste its last line into the commit body.
5. **Commit format:** `feat(dsp): add YIN f0 extractor` + blank line + `refs specs/001-audio-engine/spec.md#E001-04`.
6. **Run `make analyze` before opening a PR.** It checks spec ↔ tasks ↔ tests traceability.

## Build & test commands

| Area | Command | Runtime |
|------|---------|---------|
| Everything | `make verify` | < 1 min (no Flutter) |
| Rust DSP | `cd packages/dsp_core && cargo test` | headless |
| Python engine | `cd services/phonetic_engine && pytest -q` | headless |
| Acoustic/linguistic evals | `python evals/run_acoustic_evals.py` | headless |
| Traceability | `python tools/analyze.py` | headless |
| Flutter | `cd apps/flutter_app && flutter test` | needs Flutter SDK |

## Invariants agents keep breaking (don't)

- Do **not** add dependencies without a line in the PR explaining cost & licence. GPL is banned in `apps/` (App Store).
- Do **not** add paid APIs (constitution K-01).
- Do **not** replace per-phoneme feedback with a percentage (C-04).
- Do **not** do DSP in Dart. Dart calls `dsp_core` via `flutter_rust_bridge`.
- Do **not** invent IPA. Targets come from `services/phonetic_engine/phonetic_engine/data/cube_lexicon.tsv`.
- Do **not** edit golden fixtures to make a test pass. Fixtures change only via a PR labelled `golden-data`.
- Do **not** "improve" things outside the current task. Note them in `specs/NNN/notes.md`.

## Code style

- Rust: `cargo fmt`, `cargo clippy -D warnings`, no `unsafe` outside `ffi.rs`, no allocation in per-frame hot loops.
- Python: 3.11+, type hints everywhere, pure functions in `alignment.py` / `markers.py`, I/O only in `app.py`.
- Dart: `flutter analyze` clean, state in plain immutable classes, no business logic in widgets.
