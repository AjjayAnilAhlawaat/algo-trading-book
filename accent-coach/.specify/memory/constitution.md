# Accent Coach — Product Constitution

> Status: **v1.0 — DRAFT, awaiting human sign-off.** No feature code merges until the
> owner signs the block at the bottom. Changes to this file require a PR labelled
> `constitution` and an explicit human approval.

## 1. Mission

Help Indian English speakers shift, by choice, toward **Modern Standard Southern
British English (SSBE)** as transcribed in the **CUBE** lexicon (Lindsey & Szigetvári).
The product measures *accent shift*, not intelligibility. Speakers are already
intelligible; we never imply otherwise.

## 2. Non-negotiable invariants (EARS, Ubiquitous)

| ID | Invariant |
|----|-----------|
| C-01 | The system shall use Modern SSBE, with phonetic values per the CUBE lexicon, as the sole target standard. Archaic RP forms (e.g. `[ʊə]` in *cure*, tapped /r/, `[ɛə]` for SQUARE where CUBE has `[ɛː]`) shall never be presented as targets. UI may display conventional Wells/Gimson symbols for familiarity; the target values are CUBE's. |
| C-02 | The system shall capture speech at 48 kHz mono 16-bit PCM and downsample to 16 kHz only at the phonetic-scoring boundary. |
| C-03 | The system shall keep raw audio on-device by default. Audio leaves the device only for an explicit scoring request, is never persisted server-side beyond the request lifetime, and is never used for training without a separate opt-in. |
| C-04 | The system shall present feedback as per-phoneme states (`match` / `near` / `miss`), never as a single opaque "accent score". |
| C-05 | The system shall run all real-time DSP (waveform, VAD, F0) off the UI thread in the Rust `dsp_core` crate. |
| C-06 | The system shall keep the round-trip from tap-to-play to first audible sample ≤ 50 ms on reference devices (iPhone 12, M1 Mac, Pixel 6a). |
| C-07 | The system shall function offline for every drill whose reference audio is cached; only diagnostic scoring may require network in v1. |
| C-08 | Every merged change shall reference a spec (`refs specs/NNN-…`) and pass `make verify`. |

## 3. Cost invariants (low-cost by design)

| ID | Invariant |
|----|-----------|
| K-01 | v1 shall have **zero per-request paid API dependencies**. No commercial pronunciation API, no paid TTS in the hot path. |
| K-02 | Reference audio is pre-recorded and shipped/cached once, not synthesised per request. |
| K-03 | The scoring service shall be stateless and run on a scale-to-zero host (e.g. Fly.io / Cloud Run free tier). |
| K-04 | Every scoring capability shall have an on-device fallback path planned (Phase 2: CoreML / ONNX). |

## 4. Out of scope (hard fences for agents)

- Teaching accents other than Modern SSBE (no GA, no Australian, no "neutral").
- Grammar, vocabulary, IELTS prep, fluency coaching.
- Social features, leaderboards, streak-shaming, ads.
- Accounts / login in v1 (progress is local; sync arrives in spec 006).
- Any LLM-generated linguistic judgement. Scoring is deterministic and reproducible.
- Web and Windows targets.

## 5. Change control

1. New capability → new `specs/NNN-name/` (Spec Kit flow).
2. After v1 ships → delta changes via OpenSpec (`propose → apply → archive`).
3. A spec that conflicts with this constitution is invalid until the constitution changes.

## 6. Sign-off

```
Owner: ____________________   Date: __________   Version: 1.0
```
