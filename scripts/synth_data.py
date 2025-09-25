# synth_data.py
import pandas as pd
from collector import collect_all
import random
import numpy as np

def build_dataset(n_synthetic_malicious=200, benign_from_system=0):
    # Get benign samples from current snapshot
    df = collect_all()
    if benign_from_system == 0:
        benign_samples = df.sample(min(len(df), 200)).copy()
    else:
        benign_samples = df.sample(min(len(df), benign_from_system)).copy()

    benign_samples['label'] = 0

    # synth malicious-like samples
    synth_rows = []
    for i in range(n_synthetic_malicious):
        row = {
            "pid": 10000 + i,
            "name": f"sus_agent_{i}.exe",
            "exe": f"/tmp/sus_{i}" if random.random() < 0.6 else f"/home/user/.local/bin/sus_{i}",
            "username": "user",
            "open_files": int(np.clip(np.random.normal(40,15), 1, 500)),   # high file operations
            "connections": int(np.clip(np.random.normal(20,10), 0, 200)),
            "path_in_temp": 1 if random.random() < 0.7 else 0,
            "path_in_user": 1 if random.random() < 0.8 else 0,
            "age_seconds": int(np.clip(np.random.exponential(3600), 10, 1e7)),
            "cmdline_len": int(np.clip(np.random.normal(4,2), 0, 40)),
            "suspicious_cmd_kw": 1 if random.random() < 0.7 else 0,
            "in_startup": 1 if random.random() < 0.6 else 0,
            "timestamp": pd.Timestamp.utcnow().isoformat(),
            "label": 1
        }
        synth_rows.append(row)

    synth_df = pd.DataFrame(synth_rows)
    dataset = pd.concat([benign_samples, synth_df], ignore_index=True).fillna(0)
    # convert numeric columns properly
    numeric_cols = ["open_files","connections","path_in_temp","path_in_user","age_seconds","cmdline_len","suspicious_cmd_kw","in_startup","label"]
    for c in numeric_cols:
        dataset[c] = pd.to_numeric(dataset[c], errors='coerce').fillna(0)
    dataset.to_csv("dataset.csv", index=False)
    print("Saved dataset.csv with", len(dataset), "rows")
    return dataset

if __name__ == "__main__":
    build_dataset()
