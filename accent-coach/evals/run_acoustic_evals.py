#!/usr/bin/env python3
"""Release gate: linguistic accuracy of marker detection (+ golden-audio manifest checks).

Layer 1 (runs today, CI): synthetic speaker profiles. Each profile applies Indian-English
substitutions to the CUBE target of the diagnostic passage at known rates, plus alignment
noise (random deletions / epenthetic vowels). Ground truth is known per phoneme, so we
measure per-marker precision/recall of the full scoring pipeline.

Layer 2 (activates when WAVs exist): evals/golden_audio/manifest.json — real recordings
of Indian English and Modern SSBE speakers with human labels. The acoustic analyser
(MFA + parselmouth, spec 002 plan) consumes these; until then we validate the manifest.

Exit code 0 = gate passed.
"""

from __future__ import annotations

import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "services" / "phonetic_engine"))

from phonetic_engine.lexicon import SILENT_R, diagnostic_passage  # noqa: E402
from phonetic_engine.markers import MARKERS  # noqa: E402
from phonetic_engine.scoring import score, target_phones  # noqa: E402

PRECISION_MIN = 0.95
RECALL_MIN = 0.95
SEEDS = range(20)

# marker -> (target phone -> IE substitute)
SUBS: dict[str, dict[str, str]] = {
    "schwa_reduction": {"ə": "a"},
    "retroflex_td": {"t": "ʈ", "tʰ": "ʈ", "d": "ɖ"},
    "rhoticity": {SILENT_R: "r"},
    "aspiration_ptk": {"pʰ": "p", "tʰ": "t", "kʰ": "k"},
    "diphthong_ei_ou": {"eɪ": "eː", "əʊ": "oː"},
    "vw_merger": {"v": "ʋ", "w": "ʋ"},
}
PRIORITY = [m.id for m in MARKERS]


@dataclass(frozen=True)
class Profile:
    name: str
    rates: dict[str, float]
    expected_top: str | None = None  # expected #1 lever


PROFILES = [
    Profile("ssbe_native", {}, None),
    Profile("ie_strong", {"retroflex_td": 0.9, "rhoticity": 0.95, "vw_merger": 0.8,
                          "diphthong_ei_ou": 0.8, "schwa_reduction": 0.6, "aspiration_ptk": 0.7}),
    Profile("ie_mild_rhotic_only", {"rhoticity": 0.8}, "rhoticity"),
    Profile("ie_retroflex_only", {"retroflex_td": 0.7}, "retroflex_td"),
    Profile("learner_schwa_left", {"schwa_reduction": 0.5, "vw_merger": 0.2}, "schwa_reduction"),
]


def synthesize(target: list[str], prof: Profile, rng: random.Random):
    """Return observed phones and truth labels {target_index: marker}."""
    obs: list[str] = []
    truth: dict[int, str] = {}
    for i, p in enumerate(target):
        chosen = None
        for mid in PRIORITY:
            sub = SUBS[mid].get(p)
            if sub is not None and rng.random() < prof.rates.get(mid, 0.0):
                chosen = (mid, sub)
                break
        if chosen:
            truth[i] = chosen[0]
            obs.append(chosen[1])
        elif p == SILENT_R:
            pass  # SSBE: silent
        elif rng.random() < 0.02 and not any(p in s for s in SUBS.values()):
            pass  # recogniser deletion of an unrelated phone
        else:
            obs.append(p)
        if rng.random() < 0.02 and p not in ("ə", SILENT_R):
            obs.append("ə")  # epenthetic vowel noise
    return obs, truth


def predicted(text: str, obs: list[str]) -> tuple[dict[int, str], list[str]]:
    res = score(text, obs)
    pred: dict[int, str] = {}
    ti = -1
    for tok in res.tokens:
        if tok.target is not None:
            ti += 1
            if tok.state == "miss" and tok.marker:
                pred[ti] = tok.marker
    return pred, res.top_levers


def run_synthetic() -> bool:
    text = diagnostic_passage()
    target = target_phones(text)
    tp = {m: 0 for m in SUBS}
    fp = {m: 0 for m in SUBS}
    fn = {m: 0 for m in SUBS}
    lever_ok, lever_n = 0, 0

    for prof in PROFILES:
        for seed in SEEDS:
            rng = random.Random(f"{prof.name}:{seed}")
            obs, truth = synthesize(target, prof, rng)
            pred, levers = predicted(text, obs)
            for i, m in pred.items():
                if truth.get(i) == m:
                    tp[m] += 1
                else:
                    fp[m] += 1
            for i, m in truth.items():
                if pred.get(i) != m:
                    fn[m] += 1
            if prof.expected_top is not None:
                lever_n += 1
                lever_ok += bool(levers) and levers[0] == prof.expected_top
            if prof.name == "ssbe_native" and pred:
                print(f"  ✕ false positives on native speech (seed {seed}): {pred}")

    ok = True
    print(f"{'marker':<18}{'TP':>6}{'FP':>5}{'FN':>5}{'prec':>8}{'recall':>8}")
    for m in SUBS:
        p = tp[m] / (tp[m] + fp[m]) if tp[m] + fp[m] else 1.0
        r = tp[m] / (tp[m] + fn[m]) if tp[m] + fn[m] else 1.0
        flag = "" if p >= PRECISION_MIN and r >= RECALL_MIN else "  ✕ below gate"
        ok &= not flag
        print(f"{m:<18}{tp[m]:>6}{fp[m]:>5}{fn[m]:>5}{p:>8.3f}{r:>8.3f}{flag}")
    lever_acc = lever_ok / lever_n
    print(f"top-1 lever accuracy on single-feature profiles: {lever_acc:.3f} ({lever_ok}/{lever_n})")
    ok &= lever_acc >= 0.95
    return ok


def check_golden_manifest() -> bool:
    manifest = ROOT / "evals" / "golden_audio" / "manifest.json"
    data = json.loads(manifest.read_text("utf-8"))
    required = {"id", "file", "speaker_group", "gender", "text", "labels"}
    ok = True
    present = 0
    for item in data["recordings"]:
        missing = required - item.keys()
        if missing:
            print(f"  ✕ {item.get('id')}: missing {missing}")
            ok = False
        if (manifest.parent / item["file"]).exists():
            present += 1
    print(f"golden audio: {present}/{len(data['recordings'])} WAVs present "
          f"(target {data['target_count']}); acoustic layer {'ACTIVE' if present else 'pending curation'}")
    return ok


def main() -> int:
    print("== Layer 1: synthetic linguistic gate ==")
    a = run_synthetic()
    print("\n== Layer 2: golden audio manifest ==")
    b = check_golden_manifest()
    print("\nGATE:", "PASS" if a and b else "FAIL")
    return 0 if a and b else 1


if __name__ == "__main__":
    sys.exit(main())
