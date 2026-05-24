# Analysis Integration

This document describes how the notebook analyses were converted into reusable modules and how to use the CLI and API to run them.

## Modules

Converted notebooks are available under `src/analysis`:

- `preprocessing.py` — signal loading, filtering, ICA, HRV extraction
- `separation.py` — ICA separation wrapper
- `features.py` — sample entropy and spectral LF/HF wrapper
- `demo_interface.py` — demo payloads
- `clustering.py` — simple KMeans wrapper
- `visualization.py` — expected development curve helper
- `interactive.py` — interactive session state helper
- `exploration.py` — small development helpers

## CLI

Run a local analysis from CSV or DB:

```bash
python scripts/run_analysis.py --file path/to/ecg.csv --patient PT_001 --weeks 32
# or
python scripts/run_analysis.py --db path/to/neuro_genomic.db
```

## API

The FastAPI endpoint `/api/v1/upload` accepts a multipart `file` upload and form fields `gestational_weeks` and `patient_id`.

Example (curl):

```bash
curl -F "file=@sample_ecg.csv" -F "gestational_weeks=32" -F "patient_id=PT_001" http://localhost:8000/api/v1/upload
```

A `file_id` will be returned; query `/api/v1/analysis/{file_id}` for results.

## Frontend

The React frontend was hooked to POST to `/api/v1/upload` from the Analysis upload UI. Set `VITE_API_URL` in `.env` for a different backend host.

## Tests

Run pytest to execute minimal integration tests:

```bash
pytest -q
```

"