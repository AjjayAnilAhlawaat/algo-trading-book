// Pure, immutable drill state machine. No Flutter imports: testable headlessly.
// refs specs/001-audio-engine T011, specs/004-blind-shadowing-studio E004-02/03/05/06.

enum DrillPhase { idle, playing, shadowing, review, interrupted }

enum DrillCommand { playPause, record, loop, toggleTranscript, slower, faster, audioFocusLost, voiceTimeout, takeEnded }

class DrillState {
  const DrillState({
    this.phase = DrillPhase.idle,
    this.speed = 1.0,
    this.looping = false,
    this.transcriptVisible = false, // E004-01: hidden by default
    this.showNoVoiceHint = false,
    this.lowBandwidthInput = false,
  });

  static const minSpeed = 0.75;
  static const maxSpeed = 1.0;
  static const speedStep = 0.05;

  final DrillPhase phase;
  final double speed;
  final bool looping;
  final bool transcriptVisible;
  final bool showNoVoiceHint;
  final bool lowBandwidthInput;

  DrillState copyWith({
    DrillPhase? phase,
    double? speed,
    bool? looping,
    bool? transcriptVisible,
    bool? showNoVoiceHint,
    bool? lowBandwidthInput,
  }) =>
      DrillState(
        phase: phase ?? this.phase,
        speed: speed ?? this.speed,
        looping: looping ?? this.looping,
        transcriptVisible: transcriptVisible ?? this.transcriptVisible,
        showNoVoiceHint: showNoVoiceHint ?? this.showNoVoiceHint,
        lowBandwidthInput: lowBandwidthInput ?? this.lowBandwidthInput,
      );

  /// E004-03: clamp to [0.75, 1.0] in 0.05 steps, rounding away float drift.
  static double _snap(double s) {
    final steps = ((s - minSpeed) / speedStep).round();
    return (minSpeed + steps * speedStep).clamp(minSpeed, maxSpeed);
  }

  DrillState reduce(DrillCommand c) {
    switch (c) {
      case DrillCommand.playPause:
        return switch (phase) {
          DrillPhase.playing || DrillPhase.shadowing => copyWith(phase: DrillPhase.idle, showNoVoiceHint: false),
          _ => copyWith(phase: DrillPhase.playing),
        };
      case DrillCommand.record:
        return phase == DrillPhase.shadowing
            ? copyWith(phase: DrillPhase.review, showNoVoiceHint: false)
            : copyWith(phase: DrillPhase.shadowing, showNoVoiceHint: false);
      case DrillCommand.loop:
        return copyWith(looping: !looping);
      case DrillCommand.toggleTranscript:
        return copyWith(transcriptVisible: !transcriptVisible);
      case DrillCommand.slower:
        return copyWith(speed: _snap(speed - speedStep));
      case DrillCommand.faster:
        return copyWith(speed: _snap(speed + speedStep));
      case DrillCommand.audioFocusLost: // E001-11: pause, resume only on user action
        return phase == DrillPhase.idle ? this : copyWith(phase: DrillPhase.interrupted, showNoVoiceHint: false);
      case DrillCommand.voiceTimeout: // E004-06: hint, never stop playback
        return phase == DrillPhase.shadowing ? copyWith(showNoVoiceHint: true) : this;
      case DrillCommand.takeEnded:
        return phase == DrillPhase.shadowing ? copyWith(phase: DrillPhase.review, showNoVoiceHint: false) : this;
    }
  }

  /// E001-10: input sample rate reported by the platform layer.
  DrillState withInputSampleRate(int hz) => copyWith(lowBandwidthInput: hz < 16000);

  /// Next phrase: transcript re-hidden (E004-02 reveals for that phrase only).
  DrillState nextPhrase() => copyWith(phase: DrillPhase.idle, transcriptVisible: false, showNoVoiceHint: false);
}
