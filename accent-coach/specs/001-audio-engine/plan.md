# 001 — Technical Plan

## Module boundaries

```
Flutter UI (Dart) ──► AudioController (Dart, state only)
     │                     │
     │ frb stream          ├─► flutter_soloud   (playback, loop, speed)
     ▼                     └─► record / platform channel (48 kHz PCM capture)
dsp_core (Rust) ◄── PCM frames (i16, 960 samples = 20 ms)
  ├─ frame::rms           → amplitude envelope
  ├─ vad::Vad             → speech/non-speech, adaptive floor
  ├─ pitch::yin           → Option<f32> F0 per frame
  ├─ calibrate::Profile   → noise floor + median F0
  └─ resample::to_16k     → only for scoring payloads
```

## Data flow per 20 ms frame
1. Platform capture → `Int16List(960)` → `dsp_core::process_frame` via frb (zero-copy where supported).
2. Returns `FrameFeatures { rms_db, is_speech, f0_hz: Option<f32>, semitones: Option<f32> }`.
3. Dart pushes into a ring buffer; `CustomPainter` renders at display refresh rate.

## Why these choices (cost & speed)
- **YIN, not pYIN, for v1:** O(N·τ) per frame, no HMM, deterministic, < 0.3 ms per frame. pYIN's Viterbi smoothing is deferred to the offline analyser.
- **Energy + zero-crossing VAD:** no model download (saves app size), good enough with calibration. WebRTC VAD is a drop-in later.
- **Linear-phase windowed-sinc resampler** for 48→16 kHz (exact 3:1 decimation, no external crate).
- **No external Rust deps** in `dsp_core` → tiny binaries, trivial 16 KB page alignment on Android.

## Contracts
- `contracts/dsp_core_ffi.md` — Rust ↔ Dart structs (frozen).
- `contracts/scoring.openapi.yaml` — client ↔ phonetic engine (shared with 002).
