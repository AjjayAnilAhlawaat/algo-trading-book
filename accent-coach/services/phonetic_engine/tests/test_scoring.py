"""EARS acceptance tests for spec 002. Test names cite requirement IDs."""

from __future__ import annotations

import json

import pytest

from phonetic_engine.alignment import align
from phonetic_engine.lexicon import SILENT_R, Lexicon, diagnostic_passage, load_default_lexicon
from phonetic_engine.markers import MARKERS
from phonetic_engine.scoring import score, target_phones

SENT = "the water is very hot"
# ð ə | w ɔː t ə (r) | ɪ z | v e r i | h ɒ t
SSBE = ["ð", "ə", "w", "ɔː", "t", "ə", "ɪ", "z", "v", "e", "r", "i", "h", "ɒ", "t"]
IE = ["d̪", "ə", "ʋ", "ɔː", "ʈ", "ə", "r", "ɪ", "z", "ʋ", "e", "r", "i", "h", "ɒ", "ʈ"]


def states(res):
    return [(t.target, t.observed, t.state, t.marker) for t in res.tokens]


def test_lexicon_loads_and_is_consistent():
    lex = load_default_lexicon()
    assert len(lex.entries) > 50
    assert lex.lookup("Water") == ("w", "ɔː", "t", "ə", SILENT_R)


def test_lexicon_rejects_duplicates_and_bad_lines():
    with pytest.raises(ValueError, match="duplicate"):
        Lexicon.parse("a\tə\na\tə")
    with pytest.raises(ValueError, match="expected"):
        Lexicon.parse("broken line")


def test_e002_04_native_ssbe_all_match():
    res = score(SENT, SSBE)
    assert all(t.state == "match" for t in res.tokens), states(res)
    assert res.top_levers == []


def test_e002_05_known_substitutes_are_miss_with_marker():
    res = score(SENT, IE)
    got = {(t.target, t.observed): (t.state, t.marker) for t in res.tokens}
    assert got[("w", "ʋ")] == ("miss", "vw_merger")
    assert got[("v", "ʋ")] == ("miss", "vw_merger")
    assert got[("t", "ʈ")] == ("miss", "retroflex_td")
    assert got[(SILENT_R, "r")] == ("miss", "rhoticity")
    # Dental /ð/ → [d̪] is not one of the six markers: near, not miss.
    assert got[("ð", "d̪")] == ("near", None)


def test_e002_05_pronounced_r_in_very_is_not_rhoticity():
    res = score(SENT, IE)
    very_r = [t for t in res.tokens if t.word == "very" and t.target == "r"]
    assert very_r and very_r[0].state == "match"


def test_e002_05_tips_only_on_non_match():
    res = score(SENT, IE)
    for t in res.tokens:
        assert (t.tip is not None) == (t.marker is not None and t.state != "match")


def test_e002_06_levers_ranked_by_weighted_impact():
    text = diagnostic_passage()
    target = target_phones(text)
    # Learner who only makes rhotic r and retroflex t/d errors.
    obs: list[str] = []
    for p in target:
        if p == SILENT_R:
            obs.append("r")
        elif p in ("t", "tʰ"):
            obs.append("ʈ")
        elif p == "d":
            obs.append("ɖ")
        else:
            obs.append(p)
    res = score(text, obs)
    assert res.top_levers[:2] == ["retroflex_td", "rhoticity"]
    by = {m.marker: m for m in res.markers}
    assert by["rhoticity"].rate == 1.0
    assert by["retroflex_td"].rate == 1.0
    assert by["schwa_reduction"].occurrences == 0


def test_e002_06_at_most_three_levers():
    text = diagnostic_passage()
    subs = {SILENT_R: "r", "t": "ʈ", "d": "ɖ", "v": "ʋ", "w": "ʋ", "eɪ": "eː", "əʊ": "oː", "ə": "a",
            "pʰ": "p", "kʰ": "k", "tʰ": "t"}
    obs = [subs.get(p, p) for p in target_phones(text)]
    res = score(text, obs)
    assert len(res.top_levers) == 3
    assert len(set(res.top_levers)) == 3


def test_e002_07_deterministic_byte_identical():
    a = json.dumps(score(SENT, IE).to_dict(), ensure_ascii=False, sort_keys=True)
    for _ in range(5):
        assert json.dumps(score(SENT, IE).to_dict(), ensure_ascii=False, sort_keys=True) == a


def test_e002_08_unknown_word_skipped_and_reported():
    res = score("the zyzzyva water", ["ð", "ə", "w", "ɔː", "t", "ə"])
    assert res.unknown_words == ["zyzzyva"]
    assert all(t.state == "match" for t in res.tokens)


def test_e002_09_marker_with_few_opportunities_excluded():
    # "the water" has only one (r) opportunity → rhoticity can't be a lever.
    res = score("the water", ["ð", "ə", "w", "ɔː", "t", "ə", "r"])
    assert "rhoticity" not in res.top_levers
    assert {m.marker: m.occurrences for m in res.markers}["rhoticity"] == 1


def test_e002_01_passage_has_five_opportunities_per_marker():
    res = score(diagnostic_passage(), target_phones(diagnostic_passage()))
    assert res.unknown_words == []
    for m in res.markers:
        assert m.opportunities >= 5, m


def test_e002_03_exactly_six_markers():
    assert [m.id for m in MARKERS] == [
        "schwa_reduction", "retroflex_td", "rhoticity", "aspiration_ptk", "diphthong_ei_ou", "vw_merger"
    ]


def test_alignment_handles_deletions_and_insertions():
    pairs = align(["k", "æ", "t"], ["k", "æ"])
    assert pairs == [(0, 0), (1, 1), (2, None)]
    pairs = align(["k", "æ", "t"], ["k", "æ", "t", "ə"])
    assert pairs[-1] == (None, 3)


def test_alignment_empty_inputs():
    assert align([], []) == []
    assert align(["a"], []) == [(0, None)]
    assert align([], ["a"]) == [(None, 0)]


def test_alignment_prefers_known_substitute_over_gaps():
    assert align(["v", "e", "t"], ["ʋ", "e", "ʈ"]) == [(0, 0), (1, 1), (2, 2)]
