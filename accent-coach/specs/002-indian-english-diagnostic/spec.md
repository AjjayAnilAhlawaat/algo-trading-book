# 002 — Indian English Diagnostic

Status: **Specified** (plan pending) · Milestone: M1

## Learner story
In under 3 minutes I read a short passage and speak freely, then see my top 3
changes that will move me most toward Modern SSBE, with exact words highlighted.

## Markers scored (v1 — exactly these, no more)

| Marker id | Feature | Indian English typical | SSBE target |
|-----------|---------|------------------------|-------------|
| `retroflex_td` | Alveolar stops | `ʈ ɖ` | `t d` |
| `aspiration_ptk` | Aspirated initial voiceless stops | `p t k` (unaspirated) | `pʰ tʰ kʰ` |
| `rhoticity` | Non-rhotic coda /r/ | `r` / `ɻ` after vowel | ∅ (no r) |
| `vw_merger` | /v/–/w/ contrast | `ʋ` for both | `v` vs `w` |
| `diphthong_ei_ou` | FACE / GOAT glides | `eː oː` monophthongs | `eɪ əʊ` |
| `schwa_reduction` | Unstressed vowel reduction | full vowel `a e o` | `ə` |

## Requirements (EARS)

| ID | Type | Requirement |
|----|------|-------------|
| E002-01 | Event | When the user starts the diagnostic, the system shall present a 60 s read-aloud passage containing ≥ 5 opportunities for each marker. |
| E002-02 | Event | When the read-aloud ends, the system shall present a 60 s unscripted prompt. |
| E002-03 | State | While in the diagnostic, the system shall score only the six markers above. |
| E002-04 | Ubiquitous | The system shall align observed phonemes against CUBE targets with deterministic global alignment (Needleman–Wunsch). |
| E002-05 | Ubiquitous | The system shall label each target phoneme `match`, `near` or `miss`, where `miss` means the observed phone is the known Indian-English substitute. |
| E002-06 | Event | When scoring completes, the system shall rank markers by impact = rate × frequency weight and show the top 3 as "levers". |
| E002-07 | Ubiquitous | Given identical input, the system shall return byte-identical output. |
| E002-08 | Unwanted | If a word is missing from the lexicon, then the system shall skip it, report it in `unknown_words`, and not fail the request. |
| E002-09 | Unwanted | If fewer than 3 opportunities exist for a marker, then the system shall exclude it from levers. |

## Out of scope
Prosody/intonation scoring, free-speech ASR quality tuning, other L1 backgrounds, any numeric overall score.
