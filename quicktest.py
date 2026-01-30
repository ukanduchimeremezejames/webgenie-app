#!/usr/bin/env python
"""
Quick test script to verify the backend is working.
Run this after starting the server and Celery worker.
"""

import requests
import json
import time
import pandas as pd
import numpy as np
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

def create_sample_dataset():
    """Create a sample dataset file."""
    print("📁 Creating sample dataset...")
    
    # Create sample data
    n_genes = 100
    n_samples = 30
    
    data = np.random.randn(n_genes, n_samples)
    df = pd.DataFrame(
        data,
        index=[f"GENE_{i}" for i in range(n_genes)],
        columns=[f"SAMPLE_{i}" for i in range(n_samples)],
    )
    
    # Save to file
    file_path = Path("sample_data.csv")
    df.to_csv(file_path)
    print(f"✓ Sample dataset saved to {file_path}")
    
    return str(file_path)

def test_health():
    """Test health endpoint."""
    print("\n🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_register_dataset(file_path):
    """Test dataset registration."""
    print("\n📊 Testing dataset registration...")
    
    data = {
        "name": "test_dataset_demo",
        "description": "Demo dataset for testing",
        "dataset_type": "expression",
        "file_path": file_path,
        "genes": 100,
        "samples": 30,
    }
    
    response = requests.post(f"{BASE_URL}/datasets/", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        dataset = response.json()
        print(f"✓ Dataset registered: {dataset['id']}")
        return dataset['id']
    else:
        print(f"✗ Failed: {response.json()}")
        return None

def test_list_datasets():
    """Test dataset listing."""
    print("\n📋 Testing dataset listing...")
    
    response = requests.get(f"{BASE_URL}/datasets/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Total datasets: {data['total']}")
        for dataset in data['datasets'][:3]:
            print(f"  - {dataset['name']} ({dataset['id']})")
        return True
    else:
        print(f"✗ Failed: {response.json()}")
        return False

def test_get_dataset_schema(dataset_id):
    """Test getting dataset schema."""
    print("\n🔍 Testing dataset schema retrieval...")
    
    response = requests.get(f"{BASE_URL}/datasets/{dataset_id}/schema")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        schema = response.json()
        print(f"✓ Schema retrieved:")
        print(f"  - Rows: {schema['row_count']}")
        print(f"  - Columns: {schema['column_count']}")
        print(f"  - Columns: {', '.join(schema['columns'][:5])}...")
        return True
    else:
        print(f"✗ Failed: {response.json()}")
        return False

def test_submit_job(dataset_id):
    """Test job submission."""
    print("\n🚀 Testing job submission...")
    
    data = {
        "dataset_id": dataset_id,
        "algorithm": "GRNBoost2",
        "params": {
            "n_jobs": 2,
        },
    }
    
    response = requests.post(f"{BASE_URL}/jobs/", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        job = response.json()
        print(f"✓ Job submitted: {job['id']}")
        print(f"  - Status: {job['status']}")
        print(f"  - Algorithm: {job['algorithm']}")
        return job['id']
    else:
        print(f"✗ Failed: {response.json()}")
        return None

def test_get_job_status(job_id):
    """Test getting job status."""
    print("\n⏳ Testing job status retrieval...")
    
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        job = response.json()
        print(f"✓ Job status:")
        print(f"  - ID: {job['id']}")
        print(f"  - Status: {job['status']}")
        print(f"  - Progress: {job['progress_percent']}%")
        print(f"  - Started: {job['started_at']}")
        return job
    else:
        print(f"✗ Failed: {response.json()}")
        return None

def test_list_jobs():
    """Test job listing."""
    print("\n📋 Testing job listing...")
    
    response = requests.get(f"{BASE_URL}/jobs/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Total jobs: {data['total']}")
        for job in data['jobs'][:3]:
            print(f"  - {job['id']} ({job['status']})")
        return True
    else:
        print(f"✗ Failed: {response.json()}")
        return False

def test_list_results():
    """Test results listing."""
    print("\n📊 Testing results listing...")
    
    response = requests.get(f"{BASE_URL}/results/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Total results: {data['total']}")
        for result in data['results'][:3]:
            print(f"  - {result['id']} (Algorithm: {result['algorithm']})")
        return True
    else:
        print(f"✗ Failed: {response.json()}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🔬 WebGenie Backend - Integration Test Suite")
    print("=" * 60)
    
    try:
        # Create sample data
        file_path = create_sample_dataset()
        
        # Test health
        if not test_health():
            print("\n❌ Server is not responding. Make sure it's running:")
            print("   python -m uvicorn app.main:app --reload")
            return
        
        # Test datasets
        if not test_list_datasets():
            return
        
        dataset_id = test_register_dataset(file_path)
        if not dataset_id:
            print("\n❌ Failed to register dataset")
            return
        
        if not test_get_dataset_schema(dataset_id):
            print("\n⚠️  Could not retrieve schema")
        
        # Test jobs
        job_id = test_submit_job(dataset_id)
        if not job_id:
            print("\n❌ Failed to submit job")
            return
        
        # Check job status
        job = test_get_job_status(job_id)
        
        if not test_list_jobs():
            print("\n⚠️  Could not list jobs")
        
        if not test_list_results():
            print("\n⚠️  Could not list results")
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        print("\n📚 API Documentation: http://localhost:8000/api/docs")
        print("🏥 Health Check: http://localhost:8000/health")
        print("\n💡 Next steps:")
        print("1. Monitor job execution in another terminal:")
        print(f"   curl http://localhost:8000/api/jobs/{job_id}")
        print("2. View Celery worker logs for execution details")
        print("3. Download results once job is completed:")
        print(f"   curl http://localhost:8000/api/results/<result_id>/download/<filename>")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error! Make sure the server is running:")
        print("   python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
