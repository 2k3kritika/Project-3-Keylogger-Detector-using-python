# detector_live.py
import joblib
import pandas as pd
from collector import collect_all
import numpy as np
import os
import json

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model.pkl")
MODEL_PATH = os.path.abspath(MODEL_PATH)
THRESHOLD = 0.5   # model probability threshold for flagging

#-----------------loading allow list from the json file--------------
ALLOWLIST_FILE = "allowlist.json"
if os.path.exists(ALLOWLIST_FILE):
    with open(ALLOWLIST_FILE,"r") as f:
        allowlist = json.load(f)
    ALLOWLIST_NAMES = set(n.lower() for n in allowlist.get("names",[]))
    ALLOWLIST_PATHS = [p.lower() for p in allowlist.get("paths", [])]
else:
    ALLOWLIST_NAMES = set()
    ALLOWLIST_PATHS = []

def is_allowlisted(name, exe_path):
    name_low = str(name or "").lower()
    exe_low = str(exe_path or "").replace("\\","/").lower().strip()
    if name_low in ALLOWLIST_NAMES:
        return True
    for p in ALLOWLIST_PATHS:
        p_low = p.replace("\\","/").lower().strip()
        if exe_low.startswith(p_low):  # fixed typo: 'startswith'
            return True
    return False
#-----------------end of allowlist code------------------------------

clf = joblib.load(MODEL_PATH)
feature_cols = ["open_files","connections","path_in_temp","path_in_user","age_seconds","cmdline_len","suspicious_cmd_kw","in_startup"]

def score_snapshot():
    df = collect_all()

    # make sure all expected feature columns exist
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0  # fill missing features with 0
            print(f"[!] Missing feature column '{col}' filled with 0")

    try:
        X = df[feature_cols].fillna(0)
        probs = clf.predict_proba(X)[:, 1]
        df["score"] = probs
    except Exception as e:
        print("[!] Model prediction failed:", e)
        df["score"] = 0.0  # fallback so code doesn’t crash

    # filter suspicious
    suspicious = df[df["score"] >= THRESHOLD].copy()

    # apply allowlist filter
    suspicious = suspicious[~suspicious.apply(
        lambda r: is_allowlisted(
            r.get("name", ""), 
            r.get("exe", "")
        ), axis=1
    )]

    # sort only if score exists
    if "score" in suspicious.columns:
        suspicious = suspicious.sort_values("score", ascending=False)
    else:
        print("[!] No 'score' column in suspicious DataFrame, returning empty")
        suspicious = pd.DataFrame()

    return df, suspicious


if __name__ == "__main__":
    df, suspicious = score_snapshot()
    print("Top suspicious processes (score >= {:.2f}):".format(THRESHOLD))
    if suspicious.empty:
        print("No suspicious processes detected.")
    else:
        for _, r in suspicious.iterrows():
            cmdline = r.get("cmdline","") if hasattr(r,"get") else (r.cmdline if "cmdline" in r.index else "")
            exe_path = r.get("exe","") if hasattr(r,"get") else (r.exe if "exe" in r.index else "")
            
            friendly = ""
            try:
                if cmdline:
                    parts = str(cmdline).split()
                    for p in parts:
                        if p.endswith(".py") or p.endswith(".exe"):
                            friendly = os.path.basename(p)
                            break
                        if not friendly and exe_path:
                            friendly = os.path.basename(exe_path)
            except Exception:
                friendly = ""

            cmd_preview = ""
            if cmdline:
                cmd_preview = "cmdline=" + (cmdline if len(cmdline)<200 else(cmdline[:197]+"..."))

            print(f"{int(r.pid)} {r.name} ({friendly}) score={r.score:.2f} open_files={r.open_files} conns={r.connections} startup={r.in_startup} temp={r.path_in_temp}{cmd_preview}")
    
    #------------save full snapshot--------------------------
    df.to_csv("live_snapshot_scored.csv", index=False)
    print("Saved live_snapshot_scored.csv")
