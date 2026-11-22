# Accent Coach

A low-cost iOS, macOS and Android app that helps Indian English speakers move toward
**Modern Standard Southern British English (SSBE)**. Built with **Spec-Anchored Development**:
specs, tests and code change together, and machine-checked gates catch drift.

```
make verify      # Rust DSP + Python engine + linguistic eval gate + spec traceability (< 1 min)
make flutter     # needs Flutter SDK
make serve       # local scoring API at http://127.0.0.1:8000/docs
```

## Where things are

| Path | What |
|------|------|
| `.specify/memory/constitution.md` | Non-negotiables, cost rules, out-of-scope fences (**needs your sign-off**) |
| `AGENTS.md` | Rules + commands every coding agent follows |
| `DESIGN.md` | Tokens, IPA typography, adaptive layout, macOS shortcuts |
| `specs/001…004` | EARS specs; 001 & 002 have plan / tasks / contracts |
| `packages/dsp_core` | Rust: RMS, adaptive VAD, YIN F0, 48→16 kHz decimator. Zero deps. |
| `services/phonetic_engine` | Python: SSBE lexicon, Needleman–Wunsch alignment, 6-marker scoring, FastAPI |
| `evals/` | Release gate: synthetic speaker profiles now, golden audio when curated |
| `tools/analyze.py` | Spec ↔ tasks ↔ tests traceability (fails on silent drift) |
| `apps/flutter_app` | Flutter client: theme tokens, drill state machine, shadowing screen skeleton |

## Status (M0 walking skeleton, in progress)

| Area | State |
|------|-------|
| Rust DSP core | ✅ 21 tests + release perf budget (< 1 ms per 20 ms frame) |
| Scoring engine | ✅ 20 tests; eval gate precision 1.00 / recall ≥ 0.985 per marker |
| Traceability | ✅ 23/33 requirements have tests; remaining ones are device-only or later milestones |
| Flutter | ✅ Analyzer clean + drill-state/theme tests green in CI (Flutter ≥ 3.47, `material_ui`); not yet run on a device |
| Device audio, FFI, pitch canvas | ⏳ Tasks T012–T017 |
| Real golden recordings | ⏳ You record/curate them (see `evals/golden_audio/manifest.json`) |

First Flutter run: `cd apps/flutter_app && flutter create --platforms=ios,android,macos --project-name accent_coach . && rm test/widget_test.dart && flutter run -d macos`.

## Low-cost strategy (≈ $0 / month until real users)

| Cost item | Choice | Monthly |
|-----------|--------|---------|
| Pronunciation scoring | Own deterministic engine (no commercial API) | $0 |
| Real-time DSP | On-device Rust | $0 |
| Scoring host | Stateless container, scale-to-zero (Cloud Run / Fly.io free tier) | $0–5 |
| Reference audio | Record native speakers once (Fiverr/Upwork voice talent ~$150–300 one-off), ship as assets / CDN | ~$0 |
| TTS resynthesis (M3) | Deferred; on-device Piper (MIT) before any paid TTS | $0 |
| CI | GitHub Actions (free for public repos; Linux runners for everything but iOS/macOS builds) | $0 |
| Store accounts | Apple Developer $99/yr, Google Play $25 one-off | ~$8 |
| Phase 2 offline scoring | Wav2Vec2-CTC → CoreML / ONNX: removes server cost entirely | $0 |

## Workflow

Spec Kit for new capabilities: constitution → specify → clarify → plan → tasks → implement → analyze.
After v1 ships, OpenSpec delta specs (propose → apply → archive). Every commit cites its spec.
