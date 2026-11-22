PY ?= python3

.PHONY: verify dsp engine evals analyze flutter serve

## Everything that runs headless (no Flutter SDK, no devices). Must pass before every commit.
verify: dsp engine evals analyze

dsp:
	cd packages/dsp_core && cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test && cargo test --release e001_12

engine:
	cd services/phonetic_engine && $(PY) -m pytest -q

evals:
	$(PY) evals/run_acoustic_evals.py

analyze:
	$(PY) tools/analyze.py

flutter:
	cd apps/flutter_app && flutter pub get && flutter analyze && flutter test

serve:
	cd services/phonetic_engine && $(PY) -m uvicorn phonetic_engine.app:app --reload
