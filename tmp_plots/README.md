## Quick start

- Data file: place `spacewire_250919215922.xlsx` in the project root.
- Outputs: generated PDFs/CSVs are written to `output/`.

## Using uv (recommended)

- Create and sync a local env from `pyproject.toml`/`uv.lock`:
  - `uv sync`
- Run the plotting pipeline:
  - `uv run python main.py`

## Using Python venv directly

- Create venv and install deps via pip:
  - macOS/Linux:
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
    - `pip install -r requirements.txt`
    - `python3 main.py`
  - Windows (PowerShell):
    - `py -3 -m venv .venv`
    - `.venv\\Scripts\\Activate.ps1`
    - `pip install -r requirements.txt`
    - `python main.py`

## Selecting charts

- Each plot is a separate function call in `main.py:17`. Comment out the calls you don’t need.
- Clustering/PCA lives in `clustering.py` and is invoked from `main.py` with `plot_agglomerative_clustering_and_pca`.
