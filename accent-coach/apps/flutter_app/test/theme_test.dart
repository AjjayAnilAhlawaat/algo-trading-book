// refs specs/001-audio-engine T010, DESIGN.md §2
import 'package:accent_coach/theme/tokens.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('both themes expose AccentTokens', () {
    for (final b in Brightness.values) {
      expect(buildTheme(b).extension<AccentTokens>(), isNotNull);
    }
  });

  test('every phoneme state has a distinct colour and a glyph', () {
    for (final t in [AccentTokens.light, AccentTokens.dark]) {
      final colours = PhonemeState.values.map(t.forState).toSet();
      expect(colours.length, PhonemeState.values.length);
    }
    final glyphs = PhonemeState.values.map(AccentTokens.glyph).toSet();
    expect(glyphs.length, PhonemeState.values.length);
  });
}
