#!/usr/bin/env bash
set -eo pipefail
mkdir -p logs exports

echo "1) Run runner"
python3 run_churn_radar.py > logs/runner.log 2>&1 || true
echo "runner log written to logs/runner.log"

echo "2) Execute notebook headless"
jupyter nbconvert --to notebook --execute churn_radar_v0.ipynb --ExecutePreprocessor.timeout=1800 --output executed.ipynb > logs/notebook.log 2>&1 || true
echo "notebook log written to logs/notebook.log"

echo "3) Run pytest"
if command -v pytest >/dev/null 2>&1 && [ -d tests ]; then
  PYTHONPATH=. pytest -q > logs/pytest.log 2>&1 || true
  echo "pytest log written to logs/pytest.log"
else
  echo "pytest not found or tests/ absent"
fi

echo "All done. Check logs/ for details."
