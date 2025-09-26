# detector_live.py
import joblib
import pandas as pd
from collector import collect_all
import numpy as np
import os

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
            #try to show the script name/cmdline where it is possible otherwise withour this part it shows python.exe as suspicous activity
            cmdline = r.get("cmdline","") if hasattr(r,"get")else(r.cmdline if "cmdline" in r.index else "") 
            exe_path = r.get("exe","") if hasattr(r,"get")else (r.exe if "exe" in r.index else "")
            friendly = ""
            try:
                #prefer explicit script file from cmdline
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
            #prepare a short cmdline preview to avoid extra thing

            cmd_preview = ""
            if cmdline:
                cmd_preview = "cmdline=" + (cmdline if len(cmdline)<200 else(cmdline[:197]+"..."))

            print(f"{int(r.pid)} {r.name} ({friendly}) score={r.score:.2f} open_files={r.open_files} conns={r.connections} startup={r.in_startup} temp={r.path_in_temp}{cmd_preview}")
    
    #------------save full snapshot--------------------------
    df.to_csv("live_snapshot_scored.csv", index=False)
    print("Saved live_snapshot_scored.csv")
