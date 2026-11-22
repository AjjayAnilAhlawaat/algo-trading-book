# 001 — Audio Engine & Calibration

Status: **Clarified** · Milestone: M0 Walking Skeleton · Owner: —

## Learner story
As a learner, I can record myself, hear a native phrase loop without gaps, and see my
pitch move live over the native pitch curve, so practice feels immediate.

## Requirements (EARS)

| ID | Type | Requirement | Verified by |
|----|------|-------------|-------------|
| E001-01 | Ubiquitous | The system shall capture microphone input as 48 kHz mono 16-bit PCM. | `apps` integration test (device) |
| E001-02 | Ubiquitous | The system shall downsample to 16 kHz only when preparing a scoring request. | `dsp_core::resample` tests |
| E001-03 | Ubiquitous | The system shall compute a frame RMS envelope (20 ms hop) in `dsp_core`. | `dsp_core` `test_e001_03_*` |
| E001-04 | Event | When a voiced frame is received, the system shall estimate F0 in the 60–400 Hz range with ≤ 2 % error on clean periodic input. | `dsp_core` `test_e001_04_*` |
| E001-05 | Event | When a frame is unvoiced or silent, the system shall report no F0 for that frame (never 0 Hz, never interpolated). | `dsp_core` `test_e001_05_*` |
| E001-06 | State | While recording, the system shall classify each frame as speech/non-speech (VAD) using an adaptive noise floor. | `dsp_core` `test_e001_06_*` |
| E001-07 | Event | When the user starts calibration, the system shall record 3 s of room tone and 5 s of speech and store the noise floor and speaker median F0. | `dsp_core` `test_e001_07_*` |
| E001-08 | Ubiquitous | The system shall express F0 in semitones relative to the speaker median for display. | `dsp_core` `test_e001_08_*` |
| E001-09 | Event | When a loop region is set, the system shall replay it gaplessly at 0.75×–1.0× speed without pitch shift. | `apps` manual + golden |
| E001-10 | Unwanted | If input sample rate drops below 16 kHz (Bluetooth HFP), then the system shall show a non-blocking banner offering the built-in mic while keeping headphone output. | `apps` widget test |
| E001-11 | Unwanted | If audio focus is lost (call, Siri, other app), then the system shall pause capture and playback and resume only on user action. | `apps` integration test |
| E001-12 | Ubiquitous | `dsp_core` processing of a 20 ms frame shall take < 1 ms on an M1 in release mode. | `cargo bench` / perf test |

## Clarifications (resolved)

- **AirPods HFP:** iOS forces 16 kHz (or 8 kHz) when mic + A2DP coexist → E001-10.
- **macOS multi-mic:** use system default input; switching mid-drill restarts capture and recalibrates noise floor only.
- **iOS silent switch:** session category `playAndRecord` + `defaultToSpeaker`; drill audio ignores the switch by design.
- **Android:** request 48 kHz to stay on the AAudio fast path; low-latency `PerformanceMode`.

## Out of scope
Noise suppression ML, echo cancellation beyond OS defaults, stereo, recording export, scoring.
