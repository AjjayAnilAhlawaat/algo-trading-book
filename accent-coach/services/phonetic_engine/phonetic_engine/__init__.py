"""Accent Coach phonetic engine — deterministic Modern SSBE accent-shift scoring.

refs specs/002-indian-english-diagnostic/spec.md
"""

from .lexicon import Lexicon, load_default_lexicon
from .scoring import score

__all__ = ["Lexicon", "load_default_lexicon", "score"]
__version__ = "1.0.0"
