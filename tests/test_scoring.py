import numpy as np
import pandas as pd
try:
    from run_churn_radar import compute_features
except Exception:
    # fallback to import by path when PYTHONPATH isn't set in test runner
    import importlib.util
    import sys
    from pathlib import Path
    spec = importlib.util.spec_from_file_location('run_churn_radar', str(Path(__file__).resolve().parents[1] / 'run_churn_radar.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules['run_churn_radar'] = module
    spec.loader.exec_module(module)
    compute_features = module.compute_features


def make_sample():
    return pd.DataFrame({
        'CustomerID': ['C1','C2','C3'],
        'OrderCount': [0, 5, 20],
        'CashbackAmount': [0, 50, 300],
        'CouponUsed': [0,1,2],
        'OrderAmountHikeFromlastYear': [0, 100, 500],
        'HourSpendOnApp': [0, 10, 40],
        'NumberOfDeviceRegistered': [1,2,3],
        'SatisfactionScore': [5,3,1],
        'Complain': [0,0,1],
        'Tenure': [1,12,36],
        'DaySinceLastOrder': [1,20,90],
    })


def test_compute_features_ranges():
    df = make_sample()
    out = compute_features(df)
    assert 'churn_risk' in out.columns
    assert 'value_score' in out.columns
    # churn risk should be between 0 and 10
    assert out['churn_risk'].min() >= 0 and out['churn_risk'].max() <= 10
    # value score between 0 and 10
    assert out['value_score'].min() >= 0 and out['value_score'].max() <= 10
