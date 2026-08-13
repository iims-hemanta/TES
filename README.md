# 360° Teaching Evaluation System (TES)

A Streamlit-based web application for generating standardized 1-page PDF scorecards from multi-source 360° teaching evaluations.

## Overview

The TES app ingests:
- **Student survey responses** (Excel `.xlsx`/`.xls`)
- **Self, Peer, and Superior assessment forms** (PDF)

It then produces a polished, single-page PDF scorecard per faculty member with:
- A diamond-shaped radar chart of stakeholder ratings
- A 7-dimension Teaching Engagement Assessment Scale (D1–D7)
- A 360° weighted average and classification level
- A calculation summary block

## Project Structure

```
TES/
├── src/
│   ├── __init__.py
│   ├── app.py              # Main Streamlit application entry point
│   ├── pdf_parser.py       # PDF score extraction utilities
│   ├── radar_chart.py      # Radar chart generation
│   ├── scorecard.py        # ReportLab PDF scorecard engine
│   └── config.py           # Configuration constants
├── tests/
│   ├── __init__.py
│   ├── test_pdf_parser.py
│   ├── test_radar_chart.py
│   └── test_scorecard.py
├── config/
│   └── settings.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10+
- pip (or uv, poetry)

## Installation

### Option A: Using pip (editable install)

```bash
cd /Users/hemanta/Desktop/TES
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Option B: Using uv (faster)

```bash
cd /Users/hemanta/Desktop/TES
uv venv
uv pip install -e ".[dev]"
```

## Running the App

```bash
# After installation
tes-app
# or
streamlit run src/app.py
```

Open your browser to `http://localhost:8501`.

## Development

### Install dev dependencies

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Lint & format

```bash
ruff check src/
black src/
mypy src/
```

## Configuration

Copy `.env.example` to `.env` and adjust values as needed:

```bash
cp .env.example .env
```

## License

MIT
