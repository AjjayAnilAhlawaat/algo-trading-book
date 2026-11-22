// Design tokens — single source: DESIGN.md §2. refs specs/001-audio-engine T010.
import 'package:flutter/material.dart';

enum PhonemeState { match, near, miss }

@immutable
class AccentTokens extends ThemeExtension<AccentTokens> {
  const AccentTokens({
    required this.bg,
    required this.surface,
    required this.ink,
    required this.inkMuted,
    required this.accent,
    required this.stateMatch,
    required this.stateNear,
    required this.stateMiss,
    required this.pitchRef,
    required this.wave,
  });

  final Color bg, surface, ink, inkMuted, accent;
  final Color stateMatch, stateNear, stateMiss, pitchRef, wave;

  static const light = AccentTokens(
    bg: Color(0xFFFBFAF7),
    surface: Color(0xFFFFFFFF),
    ink: Color(0xFF1D1D1F),
    inkMuted: Color(0xFF6E6E73),
    accent: Color(0xFF0A5FD8),
    stateMatch: Color(0xFF1F8A4C),
    stateNear: Color(0xFFB7791F),
    stateMiss: Color(0xFFC0362C),
    pitchRef: Color(0x998E8E93),
    wave: Color(0x401D1D1F),
  );

  static const dark = AccentTokens(
    bg: Color(0xFF121212),
    surface: Color(0xFF1C1C1E),
    ink: Color(0xFFF2F2F7),
    inkMuted: Color(0xFF9A9AA0),
    accent: Color(0xFF4C8DFF),
    stateMatch: Color(0xFF34C759),
    stateNear: Color(0xFFFFB340),
    stateMiss: Color(0xFFFF6961),
    pitchRef: Color(0x99AEAEB2),
    wave: Color(0x4DF2F2F7),
  );

  Color forState(PhonemeState s) => switch (s) {
        PhonemeState.match => stateMatch,
        PhonemeState.near => stateNear,
        PhonemeState.miss => stateMiss,
      };

  /// Never colour-only (WCAG 1.4.1, DESIGN.md §2).
  static String glyph(PhonemeState s) => switch (s) {
        PhonemeState.match => '✓',
        PhonemeState.near => '~',
        PhonemeState.miss => '✕',
      };

  @override
  AccentTokens copyWith() => this;

  @override
  AccentTokens lerp(ThemeExtension<AccentTokens>? other, double t) {
    if (other is! AccentTokens) return this;
    Color l(Color a, Color b) => Color.lerp(a, b, t)!;
    return AccentTokens(
      bg: l(bg, other.bg),
      surface: l(surface, other.surface),
      ink: l(ink, other.ink),
      inkMuted: l(inkMuted, other.inkMuted),
      accent: l(accent, other.accent),
      stateMatch: l(stateMatch, other.stateMatch),
      stateNear: l(stateNear, other.stateNear),
      stateMiss: l(stateMiss, other.stateMiss),
      pitchRef: l(pitchRef, other.pitchRef),
      wave: l(wave, other.wave),
    );
  }
}

ThemeData buildTheme(Brightness b) {
  final t = b == Brightness.light ? AccentTokens.light : AccentTokens.dark;
  return ThemeData(
    brightness: b,
    useMaterial3: true,
    scaffoldBackgroundColor: t.bg,
    colorScheme: ColorScheme.fromSeed(seedColor: t.accent, brightness: b, surface: t.surface),
    extensions: [t],
  );
}

extension AccentTheme on BuildContext {
  AccentTokens get tokens => Theme.of(this).extension<AccentTokens>()!;
}
