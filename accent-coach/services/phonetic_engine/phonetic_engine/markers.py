"""The six Indian-English → Modern SSBE transfer markers (spec 002, E002-03).

Pure data + pure functions. Weights are seed priors (approximate relative frequency of
each opportunity in running SSBE speech); recalibrate from corpus counts in spec 006.
"""

from __future__ import annotations

from dataclasses import dataclass

from .lexicon import SILENT_R

RHOTICS = frozenset({"r", "ɹ", "ɻ", "ɾ"})
VOWELS = frozenset(
    "ɪ e æ ʌ ɒ ʊ ə i iː ɜː ɑː ɔː uː eɪ aɪ ɔɪ əʊ aʊ ɪə eə ʊə "
    "a o eː oː ɛ ɔ ɐ oʊ u".split()
)


@dataclass(frozen=True)
class Marker:
    id: str
    label: str
    weight: float
    tip: str
    targets: frozenset[str]
    # target phone -> observed phones that are the known Indian-English substitute (=> miss)
    substitutes: dict[str, frozenset[str]]
    # target phone -> observed phones that are close but not SSBE (=> near)
    near: dict[str, frozenset[str]]


def _fs(*xs: str) -> frozenset[str]:
    return frozenset(xs)


MARKERS: tuple[Marker, ...] = (
    Marker(
        id="schwa_reduction",
        label="Weak vowels → schwa /ə/",
        weight=1.0,
        tip="Relax it to a quick, neutral 'uh'.",
        targets=_fs("ə"),
        substitutes={"ə": _fs("a", "ɐ", "e", "ɛ", "o", "ɔ", "ʌ", "ɒ", "æ", "eː", "oː")},
        near={"ə": _fs("ɪ", "ʊ")},
    ),
    Marker(
        id="retroflex_td",
        label="Alveolar /t d/, not retroflex",
        weight=0.9,
        tip="Tongue tip on the ridge behind your teeth — don't curl it back.",
        targets=_fs("t", "tʰ", "d"),
        substitutes={"t": _fs("ʈ", "ʈʰ"), "tʰ": _fs("ʈ", "ʈʰ"), "d": _fs("ɖ")},
        near={"t": _fs("t̪", "ʔ"), "tʰ": _fs("t̪"), "d": _fs("d̪")},
    ),
    Marker(
        id="rhoticity",
        label="Drop the 'r' after vowels",
        weight=0.6,
        tip="No r here — just finish (or lengthen) the vowel.",
        targets=_fs(SILENT_R),
        substitutes={SILENT_R: RHOTICS},
        near={},
    ),
    Marker(
        id="aspiration_ptk",
        label="Aspirate stressed /p t k/",
        weight=0.5,
        tip="Add a small puff of air after the sound.",
        targets=_fs("pʰ", "tʰ", "kʰ"),
        substitutes={"pʰ": _fs("p"), "tʰ": _fs("t", "t̪"), "kʰ": _fs("k")},
        near={},
    ),
    Marker(
        id="diphthong_ei_ou",
        label="Glide FACE /eɪ/ and GOAT /əʊ/",
        weight=0.5,
        tip="Make it move: /eɪ/ ends near 'ee', /əʊ/ ends near 'oo'.",
        targets=_fs("eɪ", "əʊ"),
        substitutes={"eɪ": _fs("eː", "e", "ɛː"), "əʊ": _fs("oː", "o", "ɔː")},
        near={"əʊ": _fs("oʊ", "ɔʊ")},
    ),
    Marker(
        id="vw_merger",
        label="Separate /v/ and /w/",
        weight=0.3,
        tip="/v/: top teeth touch lower lip. /w/: round lips, no teeth.",
        targets=_fs("v", "w"),
        substitutes={"v": _fs("ʋ", "w"), "w": _fs("ʋ", "v")},
        near={},
    ),
)

MARKERS_BY_ID: dict[str, Marker] = {m.id: m for m in MARKERS}
# Priority for attribution when a target belongs to several markers (e.g. tʰ): order in MARKERS.


def classify(target: str | None, observed: str | None) -> tuple[str, str | None]:
    """Return (state, marker_id) for one aligned pair. Deterministic.

    state ∈ {match, near, miss}; `miss` only for a known Indian-English substitute (E002-05).
    """
    if target == SILENT_R:
        if observed is None:
            return "match", None
        if observed in RHOTICS:
            return "miss", "rhoticity"
        return "near", None
    if target is None:
        # Inserted observed phone with no target.
        return "near", None
    if observed == target:
        return "match", None
    if observed is not None:
        for m in MARKERS:
            if observed in m.substitutes.get(target, ()):
                return "miss", m.id
        for m in MARKERS:
            if observed in m.near.get(target, ()):
                return "near", m.id
    return "near", None


def opportunities_for(target: str) -> list[str]:
    return [m.id for m in MARKERS if target in m.targets]


def substitution_cost(target: str, observed: str) -> float:
    """Alignment cost used by Needleman–Wunsch. Known substitutes align cheaply."""
    if target == observed:
        return 0.0
    if target == SILENT_R:
        return 0.0 if observed in RHOTICS else 99.0
    for m in MARKERS:
        if observed in m.substitutes.get(target, ()) or observed in m.near.get(target, ()):
            return 0.4
    t_v, o_v = target in VOWELS, observed in VOWELS
    return 1.0 if t_v == o_v else 3.0
