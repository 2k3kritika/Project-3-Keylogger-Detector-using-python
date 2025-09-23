# detector_live.py
import joblib
import pandas as pd
from collector import collect_all
import numpy as np

MODEL_PATH = "model.pkl"
THRESHOLD = 0.5   # model probability threshold for flagging

clf = joblib.load(MODEL_PATH)
feature_cols = ["open_files","connections","path_in_temp","path_in_user","age_seconds","cmdline_len","suspicious_cmd_kw","in_startup"]

def score_snapshot():
    df = collect_all()
    X = df[feature_cols].fillna(0)
    probs = clf.predict_proba(X)[:,1]
    df["score"] = probs
    suspicious = df[df["score"] >= THRESHOLD].sort_values("score", ascending=False)
    return df, suspicious

if __name__ == "__main__":
    df, suspicious = score_snapshot()
    print("Top suspicious processes (score >= {:.2f}):".format(THRESHOLD))
    if suspicious.empty:
        print("No suspicious processes detected.")
    else:
        for _, r in suspicious.iterrows():
            print(f"{int(r.pid)} {r.name} score={r.score:.2f} open_files={r.open_files} conns={r.connections} startup={r.in_startup} temp={r.path_in_temp}")
    df.to_csv("live_snapshot_scored.csv", index=False)
    print("Saved live_snapshot_scored.csv")
