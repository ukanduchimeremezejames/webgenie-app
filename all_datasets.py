import requests
import json

datasets = [
    {"name": "Supplemental-GRNs-and-Priors", "description": "Supplemental gene regulatory networks and priors", "dataset_type": "benchmark", "file_path": "cskokgibbs/Supplemental-GRNs-and-Priors"},
    {"name": "MS-mouse-noGTL-cache", "description": "Multi-species mouse dataset cache without GTL", "dataset_type": "benchmark", "file_path": "cskokgibbs/MS-mouse-noGTL-hESC-HepG2-mESC-mDC-mHSC-cache"},
    {"name": "MS-mouse-noGTL", "description": "Multi-species mouse dataset without GTL", "dataset_type": "expression", "file_path": "cskokgibbs/MS-mouse-noGTL-hESC-HepG2-mESC-mDC-mHSC", "samples": 422000},
    {"name": "MS-human-noGTL-cache", "description": "Multi-species human dataset cache without GTL", "dataset_type": "benchmark", "file_path": "cskokgibbs/MS-human-noGTL-mESC-mDC-mHSC-hESC-HepG2-cache"},
    {"name": "yeast-tf-sequence-homology-cache", "description": "Yeast TF sequence homology pretokenized cache", "dataset_type": "benchmark", "file_path": "cskokgibbs/yeast-tf-sequence-homology-pretokenized-NT-cache"},
    {"name": "BEELINE-Human-Full-cache", "description": "BEELINE human full dataset pretokenized cache", "dataset_type": "benchmark", "file_path": "cskokgibbs/BEELINE-Human-Full-pre-tokenized-NT-cache"},
    {"name": "yeast-gene-sequence-homology", "description": "Yeast gene sequence homology pretokenized", "dataset_type": "expression", "file_path": "cskokgibbs/yeast-gene-sequence-homology-pretokenized-NT", "samples": 5120000},
    {"name": "yeast-tf-sequence-homology", "description": "Yeast TF sequence homology pretokenized", "dataset_type": "expression", "file_path": "cskokgibbs/yeast-tf-sequence-homology-pretokenized-NT", "samples": 2230000},
    {"name": "mouse_datasets", "description": "Collection of mouse gene expression datasets", "dataset_type": "expression", "file_path": "cskokgibbs/mouse_datasets", "metadata": {"species": "mouse"}},
    {"name": "human_datasets", "description": "Collection of human gene expression datasets", "dataset_type": "expression", "file_path": "cskokgibbs/human_datasets", "metadata": {"species": "human"}},
    {"name": "yeast-GRNs", "description": "Yeast gene regulatory networks", "dataset_type": "benchmark", "file_path": "cskokgibbs/yeast-GRNs"},
    {"name": "hESC-GRNs", "description": "Human embryonic stem cell gene regulatory networks", "dataset_type": "benchmark", "file_path": "cskokgibbs/hESC-GRNs", "samples": 28600},
    {"name": "mESC-GRNs", "description": "Mouse embryonic stem cell gene regulatory networks", "dataset_type": "benchmark", "file_path": "cskokgibbs/mESC-GRNs", "samples": 24200},
]

base_url = "http://localhost:8000/datasets/"

for dataset in datasets:
    try:
        response = requests.post(base_url, json=dataset)
        if response.status_code == 201:
            print(f"✅ Registered: {dataset['name']}")
        else:
            print(f"❌ Failed: {dataset['name']} - {response.text}")
    except Exception as e:
        print(f"❌ Error registering {dataset['name']}: {e}")