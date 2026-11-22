# 002 — Tasks

## Deterministic scoring core (headless, CI)
- [x] T101 Seed Modern SSBE lexicon + loader with `(r)` / aspiration annotations — verify: `pytest -k lexicon`
- [x] T102 Needleman–Wunsch aligner (E002-04) — verify: `pytest -k "alignment or e002_04"`
- [x] T103 Six-marker classifier, match/near/miss (E002-03, E002-05) — verify: `pytest -k "e002_03 or e002_05"`
- [x] T104 Impact ranking + top-3 levers (E002-06, E002-09) — verify: `pytest -k "e002_06 or e002_09"`
- [x] T105 Determinism (E002-07) and unknown-word handling (E002-08) — verify: `pytest -k "e002_07 or e002_08"`
- [x] T106 Diagnostic passage with ≥ 5 opportunities per marker (E002-01) — verify: `pytest -k e002_01`
- [x] T107 FastAPI `/v1/align` per OpenAPI contract — verify: `pytest tests/test_api.py`
- [x] T108 Synthetic eval gate (precision/recall ≥ 0.95) — verify: `make evals`

## Acoustic front-end (server, M1)
- [ ] T110 Montreal Forced Aligner (english_uk_mfa) wrapper → observed phones + timings
- [ ] T111 parselmouth measures: VOT for /p t k/, F1/F2 glide slope for /eɪ əʊ/, F3 dip for rhotics
- [ ] T112 Map acoustic measures → observed symbols (e.g. VOT < 30 ms → unaspirated `t`)
- [ ] T113 Unscripted 60 s prompt flow (E002-02)
- [ ] T114 Phonetician review of `cube_lexicon.tsv` (blocks release, constitution C-01)
- [ ] T115 Golden-audio layer of `run_acoustic_evals.py` active with ≥ 40 recordings
