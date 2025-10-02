import os
import json
import subprocess
from pathlib import Path


def test_runner_creates_exports(tmp_path):
    # Run the runner in a subprocess to avoid polluting test process state
    env = os.environ.copy()
    # force demo mode (no live API key)
    env.pop('OPENAI_API_KEY', None)
    env['LIVE_ONLY'] = '0'

    p = subprocess.run(['python3', 'run_churn_radar.py'], env=env, capture_output=True, text=True)
    # runner should exit normally (we allow fallback/demo)
    assert p.returncode == 0 or p.returncode is None

    exports = Path('exports')
    assert exports.exists()
    manifest = exports / 'manifest.json'
    assert manifest.exists(), 'manifest.json missing'
    with open(manifest) as f:
        data = json.load(f)
    assert 'cohorts' in data and isinstance(data['cohorts'], dict)

    # ensure at least one cohort CSV exists
    csvs = list(exports.glob('*.csv'))
    assert len(csvs) >= 1, 'No CSV exports found'
