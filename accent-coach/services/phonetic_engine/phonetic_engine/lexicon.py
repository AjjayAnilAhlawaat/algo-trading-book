"""Modern SSBE target lexicon loader. Pure, no I/O beyond reading the TSV once."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources

SILENT_R = "(r)"
_WORD_RE = re.compile(r"[a-z']+")


@dataclass(frozen=True)
class Lexicon:
    entries: dict[str, tuple[str, ...]]

    def lookup(self, word: str) -> tuple[str, ...] | None:
        return self.entries.get(word.lower())

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return _WORD_RE.findall(text.lower())

    @classmethod
    def parse(cls, tsv: str) -> "Lexicon":
        entries: dict[str, tuple[str, ...]] = {}
        for lineno, line in enumerate(tsv.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                word, phones = line.split("\t")
            except ValueError as e:
                raise ValueError(f"lexicon line {lineno}: expected word<TAB>phones") from e
            if word in entries:
                raise ValueError(f"lexicon line {lineno}: duplicate entry {word!r}")
            entries[word] = tuple(phones.split())
        return cls(entries)


@lru_cache(maxsize=1)
def load_default_lexicon() -> Lexicon:
    text = resources.files("phonetic_engine").joinpath("data/cube_lexicon.tsv").read_text("utf-8")
    return Lexicon.parse(text)


@lru_cache(maxsize=1)
def diagnostic_passage() -> str:
    return (
        resources.files("phonetic_engine")
        .joinpath("data/diagnostic_passage.txt")
        .read_text("utf-8")
        .strip()
    )
