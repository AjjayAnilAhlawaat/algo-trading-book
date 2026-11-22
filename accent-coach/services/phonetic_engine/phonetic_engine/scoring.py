"""Text + observed phonemes → per-phoneme tokens, marker summaries, top-3 levers (spec 002)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .alignment import align
from .lexicon import Lexicon, load_default_lexicon
from .markers import MARKERS, MARKERS_BY_ID, classify, opportunities_for

MIN_OPPORTUNITIES = 3  # E002-09
TOP_N = 3  # E002-06


@dataclass(frozen=True)
class Token:
    word: str
    target: str | None
    observed: str | None
    state: str
    marker: str | None
    tip: str | None


@dataclass(frozen=True)
class MarkerSummary:
    marker: str
    label: str
    occurrences: int
    opportunities: int
    rate: float
    impact: float


@dataclass(frozen=True)
class ScoreResult:
    tokens: list[Token]
    markers: list[MarkerSummary]
    top_levers: list[str]
    unknown_words: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def score(text: str, observed: list[str], lexicon: Lexicon | None = None) -> ScoreResult:
    lex = lexicon or load_default_lexicon()

    target: list[str] = []
    target_word: list[str] = []
    unknown: list[str] = []
    for w in Lexicon.tokenize(text):
        phones = lex.lookup(w)
        if phones is None:
            if w not in unknown:
                unknown.append(w)  # E002-08: skip, report, don't fail
            continue
        target.extend(phones)
        target_word.extend([w] * len(phones))

    pairs = align(target, observed)

    tokens: list[Token] = []
    last_word = target_word[0] if target_word else ""
    for ti, oi in pairs:
        t = target[ti] if ti is not None else None
        o = observed[oi] if oi is not None else None
        word = target_word[ti] if ti is not None else last_word
        if ti is not None:
            last_word = word
        state, marker = classify(t, o)
        tip = MARKERS_BY_ID[marker].tip if marker and state != "match" else None
        tokens.append(Token(word, t, o, state, marker, tip))

    opp = {m.id: 0 for m in MARKERS}
    occ = {m.id: 0 for m in MARKERS}
    for t in target:
        for mid in opportunities_for(t):
            opp[mid] += 1
    for tok in tokens:
        if tok.state == "miss" and tok.marker:
            occ[tok.marker] += 1

    summaries: list[MarkerSummary] = []
    for m in MARKERS:
        rate = occ[m.id] / opp[m.id] if opp[m.id] else 0.0
        summaries.append(
            MarkerSummary(m.id, m.label, occ[m.id], opp[m.id], round(rate, 4), round(rate * m.weight, 4))
        )

    eligible = [s for s in summaries if s.opportunities >= MIN_OPPORTUNITIES and s.occurrences > 0]
    eligible.sort(key=lambda s: (-s.impact, s.marker))
    levers = [s.marker for s in eligible[:TOP_N]]

    return ScoreResult(tokens, summaries, levers, unknown)


def target_phones(text: str, lexicon: Lexicon | None = None) -> list[str]:
    lex = lexicon or load_default_lexicon()
    out: list[str] = []
    for w in Lexicon.tokenize(text):
        out.extend(lex.lookup(w) or ())
    return out
