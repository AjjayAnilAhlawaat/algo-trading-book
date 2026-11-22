# 001 — Tasks

Legend: `[x]` done · `[ ]` todo · **verify** = command that must pass.

## Pure logic (headless, CI)
- [x] T001 Crate skeleton + `FrameFeatures` struct per contract — verify: `cargo test`
- [x] T002 `frame::rms_db` (E001-03) — verify: `cargo test e001_03`
- [x] T003 `pitch::yin` 60–400 Hz, ≤ 2 % error (E001-04) — verify: `cargo test e001_04`
- [x] T004 Unvoiced → `None` (E001-05) — verify: `cargo test e001_05`
- [x] T005 Adaptive VAD (E001-06) — verify: `cargo test e001_06`
- [x] T006 Calibration profile (E001-07) — verify: `cargo test e001_07`
- [x] T007 Hz → semitones vs median (E001-08) — verify: `cargo test e001_08`
- [x] T008 48→16 kHz decimator (E001-02) — verify: `cargo test e001_02`
- [x] T009 Per-frame perf budget (E001-12) — verify: `cargo test --release e001_12`

## Flutter + platform (needs SDK / devices)
- [x] T010 App shell, theme tokens from DESIGN.md — verify: `flutter test test/theme_test.dart`
- [x] T011 Drill state machine (pure Dart) — verify: `flutter test test/drill_state_test.dart`
- [ ] T012 flutter_rust_bridge codegen for `dsp_core` — verify: `flutter test test/ffi_smoke_test.dart`
- [ ] T013 48 kHz capture on iOS / macOS / Android (E001-01) — verify: `integration_test/capture_test.dart` on device
- [ ] T014 flutter_soloud gapless loop + speed (E001-09) — verify: manual checklist `qa/001-loop.md`
- [ ] T015 Live pitch canvas `CustomPainter` 60 fps — verify: `flutter test test/pitch_canvas_golden_test.dart`
- [ ] T016 HFP degradation banner (E001-10) — verify: `flutter test test/hfp_banner_test.dart`
- [ ] T017 Audio-focus interruption (E001-11) — verify: device integration test
