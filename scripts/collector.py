# collector.py
import psutil, platform, os, time, json
from datetime import datetime
import pandas as pd

def get_startup_paths():
    paths = []
    system = platform.system()
    home = os.path.expanduser("~")
    if system == "Windows":
        # Common user startup folder
        paths.append(os.path.join(os.getenv("APPDATA",""), r"Microsoft\Windows\Start Menu\Programs\Startup"))
    else:
        # XDG autostart, systemd user units folder is harder to detect; keep simple
        paths.append(os.path.join(home, ".config", "autostart"))
        paths.append("/etc/xdg/autostart")
    return [p for p in paths if p]

def is_in_startup(exe_path):
    for p in get_startup_paths():
        try:
            # check if a file with same name exists in startup folders (safe, just check)
            if not os.path.isdir(p):
                continue
            name = os.path.basename(exe_path)
            candidates = [os.path.join(p, name), os.path.join(p, name + ".desktop"), os.path.join(p, name + ".lnk")]
            for c in candidates:
                if os.path.exists(c):
                    return 1
        except Exception:
            continue
    return 0

def extract_process_features(proc):
    try:
        info = proc.as_dict(attrs=['pid','name','exe','cmdline','username','create_time'])
    except Exception:
        return None

    pid = info.get("pid")
    name = info.get("name") or ""
    exe = info.get("exe") or ""
    cmdline = " ".join(info.get("cmdline") or [])
    username = info.get("username") or ""
    create_time = info.get("create_time") or 0

    # safe queries: may require privileges for some fields, handle exceptions
    open_files = 0
    connections = 0
    try:
        open_files = len(proc.open_files())
    except Exception:
        open_files = -1
    try:
        conns = proc.connections(kind='inet')
        connections = len(conns)
    except Exception:
        connections = -1

    # derived features (simple, explainable)
    path_in_temp = 1 if (exe and ("temp" in exe.lower() or "tmp" in exe.lower())) else 0
    path_in_user = 1 if (exe and os.path.expanduser("~") in exe) else 0
    age_seconds = time.time() - create_time if create_time else -1
    cmdline_len = len(cmdline)
    suspicious_cmd_keywords = int(any(k in cmdline.lower() for k in ["key", "hook", "capture", "keyboard", "keystroke", "autostart"]))

    features = {
        "pid": pid,
        "name": name,
        "exe": exe,
        "username": username,
        "open_files": open_files,
        "connections": connections,
        "path_in_temp": path_in_temp,
        "path_in_user": path_in_user,
        "age_seconds": age_seconds,
        "cmdline_len": cmdline_len,
        "suspicious_cmd_kw": suspicious_cmd_keywords,
        "in_startup": is_in_startup(exe) if exe else 0,
        "timestamp": datetime.utcnow().isoformat()
    }
    return features

def collect_all():
    rows = []
    for p in psutil.process_iter():
        f = extract_process_features(p)
        if f:
            rows.append(f)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = collect_all()
    print(df[["pid","name","open_files","connections","in_startup","path_in_temp","cmdline_len","suspicious_cmd_kw"]].to_string(index=False))
    df.to_csv("telemetry_snapshot.csv", index=False)
    print("Saved telemetry_snapshot.csv")
