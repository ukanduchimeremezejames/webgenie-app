# WebGenie Backend

Production-ready FastAPI backend for Beeline GRN inference. Exposes datasets, algorithms, and pipeline runners through clean, modular API endpoints.

## Features

- ✅ FastAPI with async endpoints
- ✅ Pydantic models for all data structures
- ✅ Celery + Redis for asynchronous job orchestration
- ✅ Dataset management and validation
- ✅ GRN inference with multiple algorithms (GRNBoost2, SCENIC, PIDC, CLR, ARACNE, NES, Inferelator, pySCENIC)
- ✅ Structured JSON logging with job context
- ✅ Comprehensive test suite with pytest
- ✅ Docker and Docker Compose support
- ✅ Production-ready code structure

## Quick Start

### 1. Installation

```bash
# Clone repository
cd webgenie-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Start Redis (required for Celery)

```bash
# Option 1: Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Option 2: Using Docker Compose (starts Redis + Backend + Worker)
docker-compose up -d
```

### 3. Run Development Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000/api/docs` (Swagger UI).

### 4. Run Celery Worker (in separate terminal)

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## API Endpoints

### Datasets

- `POST /api/datasets/` - Register new dataset
- `GET /api/datasets/` - List all datasets
- `GET /api/datasets/{dataset_id}` - Get dataset details
- `GET /api/datasets/{dataset_id}/schema` - Get dataset schema
- `DELETE /api/datasets/{dataset_id}` - Delete dataset

### Jobs

- `POST /api/jobs/` - Submit inference job
- `GET /api/jobs/` - List all jobs
- `GET /api/jobs/{job_id}` - Get job status
- `GET /api/jobs/{job_id}/logs` - Get job logs
- `DELETE /api/jobs/{job_id}` - Cancel job

### Results

- `GET /api/results/` - List results
- `GET /api/results/{result_id}` - Get result details
- `GET /api/results/{result_id}/files` - List output files
- `GET /api/results/{result_id}/download/{filename}` - Download file
- `DELETE /api/results/{result_id}` - Delete result

## Project Structure

```  webgenie-backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── config.py           # Pydantic settings
│   │   ├── logging.py          # Structured logging setup
│   │   └── tasks.py            # Celery task registration
│   ├── api/
│   │   ├── datasets.py         # Dataset endpoints
│   │   ├── jobs.py             # Job endpoints
│   │   └── results.py          # Results endpoints
│   ├── services/
│   │   ├── datasets_service.py # Dataset business logic
│   │   ├── jobs_service.py     # Job management logic
│   │   ├── inference_service.py# Results management
│   │   └── runners/
│   │       ├── beeline_runner.py      # GRN inference algorithms
│   │       ├── grn_tools_runner.py    # Additional tools
│   │       └── utils.py               # Runner utilities
│   ├── models/
│   │   ├── job.py              # Job Pydantic models
│   │   ├── dataset.py          # Dataset Pydantic models
│   │   └── result.py           # Result Pydantic models
│   └── workers/
│       └── celery_app.py       # Celery configuration
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests
│   │   ├── test_datasets_service.py
│   │   ├── test_jobs_service.py
│   │   └── test_runners.py
│   └── integration/            # Integration tests
│       └── test_api.py
├── data/                       # Data directory (created at runtime)
│   ├── results/                # Job results
│   └── datasets/               # Registered datasets
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Production Docker image
├── docker-compose.yml          # Multi-container setup
└── README.md                   # This file
```

## Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Key settings:

- `ENVIRONMENT` - development/production
- `DEBUG` - Enable debug mode
- `REDIS_URL` - Redis connection URL
- `CELERY_BROKER_URL` - Celery broker URL
- `JOB_TIMEOUT` - Maximum job execution time
- `CORS_ORIGINS` - Allowed CORS origins

## Testing

Run the test suite:

```bash
# All tests
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/unit/test_datasets_service.py

# Verbose output
pytest -v
```

## Running with Docker

### Development

```bash
docker-compose up
```

This starts:
- FastAPI backend on `http://localhost:8000`
- Celery worker for async job processing
- Redis server for job queue

### Production

```bash
docker build -t webgenie-backend:latest .
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e REDIS_URL=redis://redis-host:6379 \
  webgenie-backend:latest
```

## Supported Algorithms

- **GRNBoost2** - Gradient boosting-based GRN inference
- **SCENIC** - Single-cell regulatory network inference
- **PIDC** - Partial Information Decomposition Correlation
- **CLR** - Context Likelihood of Relatedness
- **ARACNE** - Algorithm for the Reconstruction of Accurate Cellular Networks
- **NES** - Network Enhancement Strategy
- **Inferelator** - Gene regulatory network inference
- **pySCENIC** - Python implementation of SCENIC

## Development Guide

### Adding a New Algorithm

1. Implement runner in `app/services/runners/beeline_runner.py`:

```python
def _run_new_algorithm(
    data: pd.DataFrame,
    params: dict,
    output_dir: Path,
    logger_instance: logging.Logger,
) -> dict:
    """Execute new algorithm."""
    log_step(logger_instance, "NewAlgorithm", "Initializing")
    
    # Implementation here
    
    return {
        "edges_count": int(edges),
        "mean_weight": float(mean),
        "output_files": ["adjacency_matrix.csv"],
    }
```

2. Add algorithm to `settings.supported_algorithms` in `app/core/config.py`

3. Route to implementation in `run_beeline_pipeline()` function

### Adding a New Endpoint

1. Create route in appropriate module (`datasets.py`, `jobs.py`, or `results.py`)
2. Use service layer for business logic
3. Include request/response Pydantic models
4. Add to test suite

### Logging

All operations automatically include structured JSON logging:

```python
from app.core import get_logger

logger = get_logger(__name__)
logger.info("Operation", extra={"job_id": "job_123"})
```

## Performance Considerations

- Jobs are queued in Redis and processed by Celery workers
- Set `MAX_CONCURRENT_JOBS` to control parallel processing
- Large datasets should be preprocessed before registration
- Results are cached in `/data/results/{job_id}/`

## Troubleshooting

### Redis Connection Error

```
Error: Redis connection refused
```

**Solution**: Ensure Redis is running

```bash
# Check Redis status
redis-cli ping
# Should return: PONG
```

### Celery Worker Not Processing Tasks

```bash
# Check worker logs
celery -A app.workers.celery_app worker --loglevel=debug
```

### Database Corruption

```bash
# Reset local database
rm webgenie.db
```

## Security Considerations

- Enable HTTPS in production
- Validate all file uploads
- Implement authentication/authorization
- Use environment variables for sensitive configuration
- Enable CORS only for trusted domains
- Run Celery workers with restricted permissions

## Integration with Frontend

Frontend should connect to:

```javascript
const API_BASE = "http://localhost:8000/api";

// Register dataset
POST /datasets/
// Submit job
POST /jobs/
// Get job status
GET /jobs/{job_id}
// Download results
GET /results/{result_id}/download/{filename}
```

## Contributing

1. Follow PEP 8 style guide
2. Write tests for new features
3. Update documentation
4. Use type hints throughout
5. Run pytest before committing

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please refer to the main Beeline repository:
https://github.com/Murali-group/Beeline
