# Local Testing & API Bypass Guide

Welcome to the **Neuro-Genomic AI Local Bypass** environment. This guide explains how to test your full AI pipeline immediately on your local machine, circumventing the need for complex cloud infrastructure like MinIO Object Storage, Redis Message Queues, and Celery Workers.

## What is the Local Bypass?
Your application's architecture is originally designed to be asynchronous and scalable:
* **Production**: When a file is uploaded, it gets locked into MinIO/S3, and a background worker evaluates it using the models. The API responds immediately with a "Task ID", and the UI retrieves the results later.

If you don't have Docker or Cloud Services running locally, this flow will crash. 
**To solve this, the code is currently "bypassed"**:
1. **`src/api/routes/upload.py`** has been rigged to intercept the `.csv`/`.edf` upload, run the `NeuroGenomicPipeline` synchronously in your terminal's RAM immediately, and stash the calculated metrics into a global Python memory dictionary (`RESULTS_DB`).
2. **`src/api/routes/analysis.py`** has been altered to reach into that temporary `RESULTS_DB` rather than querying a PostgreSQL database.

This allows Streamlit to effortlessly load the predictions instantly on your laptop!

---

## How to Test Locally 

To fire up the environment in bypass mode, you simply need to spawn two separate terminal sessions from the root directory (`neuro-genomic-ai-main`).

### Step 1: Start the AI Backend API
Ensure your Virtual Environment is active (`venv\Scripts\activate`), then run:
```powershell
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```
*Leave this terminal open. It will print pipeline logs (e.g. Bootstrapping Gaussian Mixtures) as it receives uploads.*

### Step 2: Start the Streamlit Dashboard
Open a second terminal, activate the environment, and run:
```powershell
python -m streamlit run src/dashboard/app.py
```
*Your browser will automatically open to `http://localhost:8501`. Navigate to the **Results Viewer** tab, upload an ECG array, and hit Analyze!*

---

## Important Limitations ⚠️

Since the data is stored completely inside application RAM:
- **Data Volatility:** If you kill the `uvicorn` terminal, all past ECG analysis results are completely erased.
- **Concurrent Limits:** Running the GMM and Gradient Boosters synchronously on the main thread will lock the API. If multiple clinicians upload files at the identical microsecond, they will wait sequentially.

## Future: How to restore Production Infrastructure
When you are ready to deploy to **Microsoft Azure** or run `docker-compose`, you *must* rollback the API to use its Celery queues. 

Simply refer back to the AI assistant or replace the Synchronous execution block located in `src/api/routes/upload.py` entirely with:
```python
        s3_client.put_object(...)
        task = process_ecg_file.delay(...)
```
And restore `src/api/routes/analysis.py` to pull target results from your Redis Database URL rather than the local `RESULTS_DB`!
