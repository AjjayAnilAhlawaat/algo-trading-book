// refs specs/001-audio-engine T011, specs/004-blind-shadowing-studio
import 'package:accent_coach/drill/drill_state.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('E004-01 transcript hidden by default', () {
    expect(const DrillState().transcriptVisible, isFalse);
  });

  test('E004-02 reveal applies to current phrase only', () {
    final s = const DrillState().reduce(DrillCommand.toggleTranscript);
    expect(s.transcriptVisible, isTrue);
    expect(s.nextPhrase().transcriptVisible, isFalse);
  });

  test('E004-03 speed clamps to 0.75–1.0 in 0.05 steps', () {
    var s = const DrillState();
    for (var i = 0; i < 10; i++) {
      s = s.reduce(DrillCommand.slower);
    }
    expect(s.speed, closeTo(0.75, 1e-9));
    s = s.reduce(DrillCommand.faster);
    expect(s.speed, closeTo(0.80, 1e-9));
    for (var i = 0; i < 10; i++) {
      s = s.reduce(DrillCommand.faster);
    }
    expect(s.speed, closeTo(1.0, 1e-9));
  });

  test('E004-05 record toggles shadowing → review', () {
    final s = const DrillState().reduce(DrillCommand.record);
    expect(s.phase, DrillPhase.shadowing);
    expect(s.reduce(DrillCommand.record).phase, DrillPhase.review);
  });

  test('E004-06 voice timeout shows hint without stopping', () {
    final s = const DrillState().reduce(DrillCommand.record).reduce(DrillCommand.voiceTimeout);
    expect(s.showNoVoiceHint, isTrue);
    expect(s.phase, DrillPhase.shadowing);
  });

  test('E001-10 low-bandwidth input flagged below 16 kHz', () {
    expect(const DrillState().withInputSampleRate(8000).lowBandwidthInput, isTrue);
    expect(const DrillState().withInputSampleRate(48000).lowBandwidthInput, isFalse);
  });

  test('E001-11 audio focus loss interrupts; only user resumes', () {
    final s = const DrillState().reduce(DrillCommand.playPause).reduce(DrillCommand.audioFocusLost);
    expect(s.phase, DrillPhase.interrupted);
    expect(s.reduce(DrillCommand.playPause).phase, DrillPhase.playing);
  });
}
