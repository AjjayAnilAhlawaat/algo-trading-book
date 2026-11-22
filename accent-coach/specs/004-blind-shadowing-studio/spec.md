# 004 — Blind Shadowing Studio

Status: **Specified** · Milestone: M2

## Learner story
I listen to a native phrase with the text hidden and speak along with it, watching
my pitch curve trace the native one, so I copy rhythm and melody, not spelling.

## Requirements (EARS)

| ID | Type | Requirement |
|----|------|-------------|
| E004-01 | Event | When a drill starts, the system shall hide the transcript (blurred), start native playback within 50 ms and draw the user's live F0 over the reference contour at ≥ 60 fps. |
| E004-02 | Event | When the user presses `T` (macOS) or taps the blur, the system shall reveal the transcript for that phrase only. |
| E004-03 | Ubiquitous | Speed shall be adjustable 0.75×–1.0× in 0.05 steps without pitch shift. |
| E004-04 | Event | When a take ends, the system shall show a side-by-side A/B (native vs user) with DTW-aligned pitch and a syllable timing ratio. |
| E004-05 | State | While on macOS, the system shall support full keyboard operation (Space, R, L, T, [, ]). |
| E004-06 | Unwanted | If the user's voice is not detected for 3 s during a take, then the system shall show a gentle "we can't hear you" hint without stopping playback. |

## Out of scope
Phoneme scoring inside shadowing (uses 002 engine later), recording sharing, lyrics/karaoke mode.
