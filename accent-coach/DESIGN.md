# DESIGN.md — Accent Coach visual system

Calm, Apple-clean, content-first. Audio is the hero; chrome stays quiet.

## 1. Principles

1. **One thing per screen.** A drill screen shows the phrase, the pitch canvas and one primary action.
2. **Ear before eye.** In blind shadowing the transcript is blurred by default (spec 004).
3. **Explain, don't grade.** Phoneme chips show *what* to change, with an IPA target and a 2-word tip.
4. **Platform-native ergonomics, one visual language.**

## 2. Tokens

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `bg` | `#FBFAF7` | `#121212` | Canvas |
| `surface` | `#FFFFFF` | `#1C1C1E` | Cards |
| `ink` | `#1D1D1F` | `#F2F2F7` | Body text |
| `ink-muted` | `#6E6E73` | `#9A9AA0` | Secondary |
| `accent` | `#0A5FD8` | `#4C8DFF` | Primary action |
| `state-match` | `#1F8A4C` | `#34C759` | Phoneme matches target |
| `state-near` | `#B7791F` | `#FFB340` | Close; one feature off |
| `state-miss` | `#C0362C` | `#FF6961` | Transfer feature present |
| `pitch-ref` | `#8E8E93` @ 60% | `#AEAEB2` @ 60% | Native reference F0 curve |
| `pitch-user` | `accent` | `accent` | Learner live F0 curve |
| `wave` | `ink` @ 25% | `ink` @ 30% | Amplitude envelope |

States are never colour-only: `match ✓`, `near ~`, `miss ✕` glyphs accompany colour (WCAG 1.4.1).

## 3. Typography

- UI: system font (SF Pro / Roboto) via platform default.
- **IPA: Noto Sans (bundled subset, OFL licence)** — guaranteed coverage of `ɪ ʊ ə ɜː ɑː ɔː æ ʌ ɒ eɪ aɪ ɔɪ əʊ aʊ ɪə eə θ ð ʃ ʒ ʧ ʤ ŋ ʔ ʰ ː`.
  IPA is always wrapped in slashes `/əʊ/` and rendered at ≥ 1.15× body size.
- Scale: 13 / 15 / 17 / 22 / 28 / 34.

## 4. Layout & adaptive rules

| Width | Layout | Navigation |
|-------|--------|------------|
| < 600 (iPhone, Android phone) | Single column, primary button in thumb zone (bottom 1/3) | Bottom tab bar (iOS) / NavigationBar (Android M3) |
| 600–1024 (iPad, tablet, small Mac window) | Two panes: drill list + drill | Rail |
| > 1024 (macOS) | Sidebar + studio + inspector | Sidebar, menu bar commands |

### Platform conventions
- **iOS:** swipe-back, haptic tick on phoneme `match`, respects silent switch only for UI sounds (drill audio uses `playAndRecord`).
- **Android:** Material 3 components, predictive back, edge-to-edge.
- **macOS:** keyboard-first — `Space` play/pause, `R` record/shadow, `L` loop phrase, `T` toggle transcript blur, `[` / `]` speed −/+ 0.05×. All listed in the menu bar (*Drill* menu).

## 5. Pitch canvas

- Y axis: semitones relative to speaker median (so male/female curves overlay), range ±12 st.
- X axis: time, reference and user aligned by DTW on syllable envelope.
- Reference curve 2 pt, user curve 3 pt, 60 fps (120 on ProMotion). Unvoiced frames are gaps, never interpolated.

## 6. Motion

200 ms ease-out for state changes; no motion during recording other than the live curve. Honour Reduce Motion.
