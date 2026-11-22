"""FastAPI surface. Contract: specs/001-audio-engine/contracts/scoring.openapi.yaml.

Stateless; nothing is persisted (constitution C-03, K-03). Run: `uvicorn phonetic_engine.app:app`.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from . import __version__
from .lexicon import diagnostic_passage
from .scoring import score

app = FastAPI(title="Accent Coach Phonetic Engine", version=__version__)


class AlignRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000, examples=["the water is very hot"])
    observed: list[str] = Field(max_length=5000, examples=[["ð", "ə", "ʋ", "ɔː", "ʈ", "ə", "r"]])


class PhonemeToken(BaseModel):
    word: str
    target: str | None
    observed: str | None
    state: str
    marker: str | None
    tip: str | None


class MarkerSummaryModel(BaseModel):
    marker: str
    label: str
    occurrences: int
    opportunities: int
    rate: float
    impact: float


class AlignResponse(BaseModel):
    tokens: list[PhonemeToken]
    markers: list[MarkerSummaryModel]
    top_levers: list[str]
    unknown_words: list[str]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/v1/diagnostic/passage")
def passage() -> dict[str, str]:
    return {"text": diagnostic_passage()}


@app.post("/v1/align", response_model=AlignResponse)
def align_endpoint(req: AlignRequest) -> dict:
    return score(req.text, req.observed).to_dict()
