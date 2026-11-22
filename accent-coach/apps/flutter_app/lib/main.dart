import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'drill/drill_state.dart';
import 'theme/tokens.dart';

void main() => runApp(const AccentCoachApp());

class AccentCoachApp extends StatelessWidget {
  const AccentCoachApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Accent Coach',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(Brightness.light),
      darkTheme: buildTheme(Brightness.dark),
      home: const DrillScreen(phrase: 'Over the weekend the weather was very hot.'),
    );
  }
}

/// Walking-skeleton drill screen (spec 004 layout). Audio wiring lands in T012–T015.
class DrillScreen extends StatefulWidget {
  const DrillScreen({super.key, required this.phrase});
  final String phrase;

  @override
  State<DrillScreen> createState() => _DrillScreenState();
}

class _DrillScreenState extends State<DrillScreen> {
  DrillState _s = const DrillState();

  void _do(DrillCommand c) => setState(() => _s = _s.reduce(c));

  // E004-05 / DESIGN.md §4: keyboard-first on macOS (also works on any hardware keyboard).
  late final Map<ShortcutActivator, VoidCallback> _keys = {
    const SingleActivator(LogicalKeyboardKey.space): () => _do(DrillCommand.playPause),
    const SingleActivator(LogicalKeyboardKey.keyR): () => _do(DrillCommand.record),
    const SingleActivator(LogicalKeyboardKey.keyL): () => _do(DrillCommand.loop),
    const SingleActivator(LogicalKeyboardKey.keyT): () => _do(DrillCommand.toggleTranscript),
    const SingleActivator(LogicalKeyboardKey.bracketLeft): () => _do(DrillCommand.slower),
    const SingleActivator(LogicalKeyboardKey.bracketRight): () => _do(DrillCommand.faster),
  };

  @override
  Widget build(BuildContext context) {
    final t = context.tokens;
    final isMac = defaultTargetPlatform == TargetPlatform.macOS;
    return CallbackShortcuts(
      bindings: _keys,
      child: Focus(
        autofocus: true,
        child: Scaffold(
          appBar: AppBar(title: const Text('Blind Shadowing'), backgroundColor: t.bg),
          body: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (_s.lowBandwidthInput)
                    MaterialBanner(
                      content: const Text('Bluetooth mic is low quality. Use the built-in mic? Audio stays in your headphones.'),
                      actions: [TextButton(onPressed: () {}, child: const Text('Switch mic'))],
                    ),
                  const SizedBox(height: 12),
                  GestureDetector(
                    onTap: () => _do(DrillCommand.toggleTranscript),
                    child: AnimatedOpacity(
                      duration: const Duration(milliseconds: 200),
                      opacity: _s.transcriptVisible ? 1 : 0.12,
                      child: Text(widget.phrase, style: Theme.of(context).textTheme.headlineSmall),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(color: t.surface, borderRadius: BorderRadius.circular(16)),
                      alignment: Alignment.center,
                      child: Text('pitch canvas (T015)', style: TextStyle(color: t.inkMuted)),
                    ),
                  ),
                  if (_s.showNoVoiceHint)
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: Text("We can't hear you — speak along with the voice.", style: TextStyle(color: t.inkMuted)),
                    ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      IconButton(onPressed: () => _do(DrillCommand.slower), icon: const Icon(Icons.remove)),
                      Text('${_s.speed.toStringAsFixed(2)}×'),
                      IconButton(onPressed: () => _do(DrillCommand.faster), icon: const Icon(Icons.add)),
                      const SizedBox(width: 12),
                      IconButton(
                        onPressed: () => _do(DrillCommand.loop),
                        icon: Icon(Icons.repeat, color: _s.looping ? t.accent : t.inkMuted),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  FilledButton.icon(
                    onPressed: () => _do(DrillCommand.record),
                    icon: Icon(_s.phase == DrillPhase.shadowing ? Icons.stop : Icons.mic),
                    label: Text(_s.phase == DrillPhase.shadowing ? 'Stop' : 'Shadow'),
                  ),
                  if (isMac)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text('Space play · R shadow · L loop · T transcript · [ ] speed',
                          textAlign: TextAlign.center, style: TextStyle(color: t.inkMuted, fontSize: 13)),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
