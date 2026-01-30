# WebGenie Backend - API Reference & Examples

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently no authentication required. Add JWT/OAuth2 as needed for production.

---

## 🏥 Health Checks

### Health Check
```bash
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "app": "WebGenie Backend"
}
```

### API Info
```bash
GET /
```

**Response (200 OK):**
```json
{
  "name": "WebGenie Backend",
  "version": "1.0.0",
  "environment": "development",
  "status": "running",
  "docs": "/api/docs"
}
```

---

## 📊 Datasets API

### Register Dataset
```bash
POST /api/datasets/
Content-Type: application/json

{
  "name": "hESC_dataset",
  "description": "Human embryonic stem cells",
  "dataset_type": "expression",
  "file_path": "/data/datasets/hESC.csv",
  "genes": 1000,
  "samples": 500,
  "metadata": {
    "source": "GEO",
    "species": "human"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "dataset_a1b2c3d4",
  "name": "hESC_dataset",
  "description": "Human embryonic stem cells",
  "dataset_type": "expression",
  "file_path": "/data/datasets/hESC.csv",
  "genes": 1000,
  "samples": 500,
  "metadata": {
    "source": "GEO",
    "species": "human"
  },
  "created_at": "2024-01-27T10:00:00",
  "updated_at": "2024-01-27T10:00:00",
  "size_bytes": 5000000
}
```

### List Datasets
```bash
GET /api/datasets/?skip=0&limit=100
```

**Response (200 OK):**
```json
{
  "total": 5,
  "datasets": [
    {
      "id": "dataset_a1b2c3d4",
      "name": "hESC_dataset",
      "description": "Human embryonic stem cells",
      "dataset_type": "expression",
      "file_path": "/data/datasets/hESC.csv",
      "genes": 1000,
      "samples": 500,
      "metadata": {},
      "created_at": "2024-01-27T10:00:00",
      "updated_at": "2024-01-27T10:00:00",
      "size_bytes": 5000000
    }
  ]
}
```

### Get Dataset Details
```bash
GET /api/datasets/{dataset_id}
```

**Response (200 OK):**
```json
{
  "id": "dataset_a1b2c3d4",
  "name": "hESC_dataset",
  "description": "Human embryonic stem cells",
  "dataset_type": "expression",
  "file_path": "/data/datasets/hESC.csv",
  "genes": 1000,
  "samples": 500,
  "metadata": {},
  "created_at": "2024-01-27T10:00:00",
  "updated_at": "2024-01-27T10:00:00",
  "size_bytes": 5000000
}
```

### Get Dataset Schema
```bash
GET /api/datasets/{dataset_id}/schema
```

**Response (200 OK):**
```json
{
  "dataset_id": "dataset_a1b2c3d4",
  "columns": [
    "SAMPLE_1",
    "SAMPLE_2",
    "SAMPLE_3"
  ],
  "row_count": 1000,
  "column_count": 500,
  "dtypes": {
    "SAMPLE_1": "float64",
    "SAMPLE_2": "float64",
    "SAMPLE_3": "float64"
  }
}
```

### Delete Dataset
```bash
DELETE /api/datasets/{dataset_id}
```

**Response (204 No Content)**

---

## 🚀 Jobs API

### Submit Inference Job
```bash
POST /api/jobs/
Content-Type: application/json

{
  "dataset_id": "dataset_a1b2c3d4",
  "algorithm": "GRNBoost2",
  "params": {
    "n_jobs": 4,
    "treeMethod": "hist"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "job_xyz123abc",
  "dataset_id": "dataset_a1b2c3d4",
  "algorithm": "GRNBoost2",
  "status": "pending",
  "params": {
    "n_jobs": 4,
    "treeMethod": "hist"
  },
  "started_at": null,
  "ended_at": null,
  "progress_percent": 0,
  "error_message": null
}
```

### List Jobs
```bash
GET /api/jobs/?skip=0&limit=100
```

**Response (200 OK):**
```json
{
  "total": 3,
  "jobs": [
    {
      "id": "job_xyz123abc",
      "dataset_id": "dataset_a1b2c3d4",
      "algorithm": "GRNBoost2",
      "status": "running",
      "params": {
        "n_jobs": 4
      },
      "started_at": "2024-01-27T10:05:00",
      "ended_at": null,
      "progress_percent": 45,
      "error_message": null
    }
  ]
}
```

### Get Job Status
```bash
GET /api/jobs/{job_id}
```

**Response (200 OK):**
```json
{
  "id": "job_xyz123abc",
  "dataset_id": "dataset_a1b2c3d4",
  "algorithm": "GRNBoost2",
  "status": "completed",
  "params": {
    "n_jobs": 4
  },
  "started_at": "2024-01-27T10:05:00",
  "ended_at": "2024-01-27T10:35:00",
  "progress_percent": 100,
  "error_message": null
}
```

### Get Job Logs
```bash
GET /api/jobs/{job_id}/logs
```

**Response (200 OK):**
```json
{
  "job_id": "job_xyz123abc",
  "logs": [
    "[2024-01-27T10:05:00] Starting job",
    "[2024-01-27T10:05:10] Loading dataset...",
    "[2024-01-27T10:05:30] Loaded: 1000 genes x 500 samples",
    "[2024-01-27T10:05:31] GRNBoost2: Initializing",
    "[2024-01-27T10:05:35] GRNBoost2: Training model",
    "[2024-01-27T10:35:00] Pipeline completed",
    "[2024-01-27T10:35:00] Results saved"
  ],
  "timestamp": "2024-01-27T10:35:00"
}
```

### Cancel Job
```bash
DELETE /api/jobs/{job_id}
```

**Response (204 No Content)**

---

## 📈 Results API

### List Results
```bash
GET /api/results/?dataset_id=dataset_a1b2c3d4&algorithm=GRNBoost2&skip=0&limit=100
```

**Response (200 OK):**
```json
{
  "total": 2,
  "results": [
    {
      "id": "result_abc123xyz",
      "job_id": "job_xyz123abc",
      "dataset_id": "dataset_a1b2c3d4",
      "algorithm": "GRNBoost2",
      "summary": {
        "edges_predicted": 5000,
        "mean_weight": 0.45,
        "max_weight": 0.99,
        "min_weight": 0.01
      },
      "created_at": "2024-01-27T10:35:00",
      "updated_at": "2024-01-27T10:35:00",
      "output_files": [
        "adjacency_matrix.csv",
        "metadata.json"
      ],
      "size_bytes": 10000000
    }
  ]
}
```

### Get Result Details
```bash
GET /api/results/{result_id}
```

**Response (200 OK):**
```json
{
  "id": "result_abc123xyz",
  "job_id": "job_xyz123abc",
  "dataset_id": "dataset_a1b2c3d4",
  "algorithm": "GRNBoost2",
  "summary": {
    "edges_predicted": 5000,
    "mean_weight": 0.45,
    "max_weight": 0.99,
    "min_weight": 0.01
  },
  "created_at": "2024-01-27T10:35:00",
  "updated_at": "2024-01-27T10:35:00",
  "output_files": [
    "adjacency_matrix.csv",
    "metadata.json"
  ],
  "size_bytes": 10000000
}
```

### List Result Files
```bash
GET /api/results/{result_id}/files
```

**Response (200 OK):**
```json
{
  "result_id": "result_abc123xyz",
  "files": [
    "adjacency_matrix.csv",
    "metadata.json",
    "logs.txt"
  ]
}
```

### Download Result File
```bash
GET /api/results/{result_id}/download/adjacency_matrix.csv
```

**Response (200 OK):** Binary file download

```bash
# Example with curl
curl -O http://localhost:8000/api/results/result_abc123xyz/download/adjacency_matrix.csv
```

### Delete Result
```bash
DELETE /api/results/{result_id}
```

**Response (204 No Content)**

---

## Supported Algorithms

### Algorithm List
```
- GRNBoost2      : Gradient boosting-based GRN inference
- SCENIC         : Single-cell regulatory network inference
- PIDC           : Partial Information Decomposition Correlation
- CLR            : Context Likelihood of Relatedness
- ARACNE         : Algorithm for the Reconstruction of Accurate Cellular Networks
- NES            : Network Enhancement Strategy
- Inferelator    : Gene regulatory network inference
- pySCENIC       : Python implementation of SCENIC
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Dataset not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## cURL Examples

### Register a Dataset
```bash
curl -X POST http://localhost:8000/api/datasets/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_dataset",
    "description": "My dataset",
    "dataset_type": "expression",
    "file_path": "/path/to/data.csv",
    "genes": 1000,
    "samples": 50
  }'
```

### Submit a Job
```bash
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "dataset_xyz",
    "algorithm": "GRNBoost2",
    "params": {"n_jobs": 4}
  }'
```

### Check Job Status (polling)
```bash
while true; do
  curl http://localhost:8000/api/jobs/job_abc123 | jq .status
  sleep 5
done
```

### Download Results
```bash
curl -O http://localhost:8000/api/results/result_xyz/download/adjacency_matrix.csv
```

### List All Datasets
```bash
curl http://localhost:8000/api/datasets/ | jq
```

### Get API Documentation
```
http://localhost:8000/api/docs
```

---

## Python Examples

### Using requests library
```python
import requests
import time

BASE_URL = "http://localhost:8000/api"

# Register dataset
dataset_response = requests.post(
    f"{BASE_URL}/datasets/",
    json={
        "name": "my_dataset",
        "dataset_type": "expression",
        "file_path": "/path/to/data.csv",
        "genes": 1000,
        "samples": 50,
    }
)
dataset_id = dataset_response.json()["id"]

# Submit job
job_response = requests.post(
    f"{BASE_URL}/jobs/",
    json={
        "dataset_id": dataset_id,
        "algorithm": "GRNBoost2",
        "params": {"n_jobs": 4}
    }
)
job_id = job_response.json()["id"]

# Poll for completion
while True:
    job = requests.get(f"{BASE_URL}/jobs/{job_id}").json()
    print(f"Status: {job['status']} ({job['progress_percent']}%)")
    
    if job['status'] in ['completed', 'failed']:
        break
    
    time.sleep(5)

# Download results
if job['status'] == 'completed':
    results = requests.get(f"{BASE_URL}/results/").json()
    # Find result for this job and download files
```

---

## Rate Limiting

Currently not implemented. Add as needed for production:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/jobs/")
@limiter.limit("100/minute")
async def list_jobs(request: Request):
    ...
```

---

## Pagination

All list endpoints support pagination:

```bash
GET /api/datasets/?skip=0&limit=100
GET /api/jobs/?skip=0&limit=100
GET /api/results/?skip=0&limit=100
```

**Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

---

## Filtering

Results endpoint supports filtering:

```bash
GET /api/results/?dataset_id=dataset_xyz&algorithm=GRNBoost2
```

**Parameters:**
- `dataset_id`: Filter by dataset (optional)
- `algorithm`: Filter by algorithm (optional)

---

## WebSocket Support (Future)

For real-time job status updates:
```python
from fastapi import WebSocket

@app.websocket("/api/ws/jobs/{job_id}")
async def websocket_job_status(websocket: WebSocket, job_id: str):
    await websocket.accept()
    while True:
        job = jobs_service.get_job(job_id)
        await websocket.send_json(job)
        await asyncio.sleep(1)
```

---

## API Versioning (Future)

For future versions:
```bash
GET /api/v1/datasets/
GET /api/v2/datasets/
```

---

**For complete interactive documentation, visit:**
```
http://localhost:8000/api/docs
```
