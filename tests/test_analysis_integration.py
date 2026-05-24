import tempfile
import os
import json
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from src.api.main import app
from scripts import run_analysis


def make_sample_csv(path):
    t = np.linspace(0, 10, 5000)
    ch1 = 0.5*np.sin(2*np.pi*1.2*t) + 0.1*np.random.randn(len(t))
    ch2 = 0.4*np.sin(2*np.pi*2.4*t + 0.5) + 0.1*np.random.randn(len(t))
    df = pd.DataFrame({'time_s': t, 'ch1': ch1, 'ch2': ch2, 'fs': 500})
    df.to_csv(path, index=False)


def test_cli_run(tmp_path, capsys):
    csv = tmp_path / "sample_ecg.csv"
    make_sample_csv(csv)
    # call run_analysis as a module function
    run_analysis.run_from_file(csv, patient_id='PT_TEST', weeks=30)


def test_api_upload_and_analysis(tmp_path):
    csv = tmp_path / "sample_ecg.csv"
    make_sample_csv(csv)
    with TestClient(app) as client:
        with open(csv, 'rb') as f:
            files = {'file': ('sample_ecg.csv', f, 'text/csv')}
            data = {'gestational_weeks': '32', 'patient_id': 'PT_API'}
            resp = client.post('/api/v1/upload', files=files, data=data)
        assert resp.status_code == 200
        body = resp.json()
        assert 'file_id' in body
        file_id = body['file_id']
        # fetch analysis
        resp2 = client.get(f'/api/v1/analysis/{file_id}')
        assert resp2.status_code == 200
        j = resp2.json()
        assert j.get('file_id') == file_id
        assert 'features' in j
