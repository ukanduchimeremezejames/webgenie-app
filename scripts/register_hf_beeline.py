#!/usr/bin/env python3
"""
Download specified Beeline datasets from Hugging Face and register them
with the local WebGenie backend API by POSTing JSON with the local file path.

Usage:
  python scripts/register_hf_beeline.py

Make sure:
- The backend is running at http://localhost:8000
- You have installed: huggingface_hub, requests
- You run this script from the project root (so files go to ./data/datasets)
"""

from huggingface_hub import list_repo_files, hf_hub_download
import requests
from pathlib import Path
import os

HF_REPO = "cskokgibbs/datasets"
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
TARGET_DIR = Path("data") / "datasets"
TARGET_DIR.mkdir(parents=True, exist_ok=True)

# Keywords to match Beeline-related dataset names/files
KEYWORDS = [
    "BEELINE",
    "beeline",
    "hESC",
    "BEELINE-hESC",
    "beeline-hESC",
]


def matches(filename: str) -> bool:
    return any(k in filename for k in KEYWORDS)


def main():
    print(f"Listing files in {HF_REPO}...")
    # Try as a dataset repo first, then fallback to model repo
    try:
        files = list_repo_files(HF_REPO, repo_type="dataset")
    except Exception as e_dataset:
        try:
            files = list_repo_files(HF_REPO, repo_type="model")
        except Exception as e_model:
            print("Failed to list repo files. Ensure huggingface_hub is installed, the repo_id is correct, and you have network access or an auth token if the repo is private.")
            print(e_model)
            return

    to_download = [f for f in files if matches(f)]
    if not to_download:
        print("No matching files found with keywords:", KEYWORDS)
        print("Files in repo:\n", "\n".join(files))
        return

    print(f"Found {len(to_download)} matching files:\n", "\n".join(to_download))

    for fname in to_download:
        print(f"\nDownloading {fname}...")
        try:
            local_path = hf_hub_download(repo_id=HF_REPO, filename=fname, cache_dir=str(TARGET_DIR))
        except Exception as e:
            print(f"Failed to download {fname}: {e}")
            continue

        # hf_hub_download may place files under cache dir using repo name; ensure file is inside TARGET_DIR
        local = Path(local_path)
        if not local.exists():
            print(f"Downloaded file not found at {local}")
            continue

        # If file is not directly inside TARGET_DIR, copy it
        dest = TARGET_DIR / local.name
        if local.resolve() != dest.resolve():
            print(f"Copying {local} -> {dest}")
            import shutil

            shutil.copy(local, dest)
            local = dest

        # Build dataset payload
        payload = {
            "name": local.stem,
            "description": f"Imported from {HF_REPO}",
            "dataset_type": "expression",
            "file_path": str(local.resolve()),
            "genes": None,
            "samples": None,
            "metadata": {"source": HF_REPO, "remote_filename": fname},
        }

        print(f"Registering dataset via {API_BASE}/api/datasets/ with file_path {payload['file_path']}")
        try:
            resp = requests.post(f"{API_BASE}/api/datasets/", json=payload, timeout=30)
            print(resp.status_code, resp.text)
        except Exception as e:
            print(f"Failed to register dataset {local.name}: {e}")


if __name__ == "__main__":
    main()
