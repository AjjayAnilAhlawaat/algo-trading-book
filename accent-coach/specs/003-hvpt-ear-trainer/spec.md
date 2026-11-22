# 003 — HVPT Ear Trainer

Status: **Specified** · Milestone: M2

High-Variability Phonetic Training: hear many native voices say minimal pairs, pick
which word you heard. Perception precedes production.

## Requirements (EARS)

| ID | Type | Requirement |
|----|------|-------------|
| E003-01 | Event | When a session starts, the system shall select minimal pairs targeting the learner's top diagnostic lever (fallback: `vw_merger`). |
| E003-02 | Ubiquitous | Each item shall be voiced by one of ≥ 4 different SSBE speakers (≥ 2 female, ≥ 2 male), never the same speaker twice in a row. |
| E003-03 | Event | When the user answers, the system shall give feedback within 100 ms and replay both words once on a miss. |
| E003-04 | State | While accuracy over the last 20 items is ≥ 90 %, the system shall advance to harder contexts (word → phrase → sentence). |
| E003-05 | Ubiquitous | Scheduling shall use SM-2 spaced repetition stored locally (SQLite/Drift). |
| E003-06 | Ubiquitous | All HVPT audio shall work offline once downloaded (C-07). |

## Seed pairs (v1)
`vet/wet`, `vine/wine`, `veil/whale` · `bait/bet`, `coat/cot` · `tin (alveolar) / tin (retroflex)` for retroflex awareness.

## Out of scope
Production scoring, synthetic voices, gamification beyond a simple progress ring.
