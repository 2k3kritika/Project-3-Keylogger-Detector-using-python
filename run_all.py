"""
run_all.py - control all the required scripts for the Keylogger Detector project.

Usage:
  python run_all.py --all                     # run collect -> synth -> train -> detect
  python run_all.py --collect                 # only run collector.py
  python run_all.py --simulate --detect       # run demo simulate then run detector
  python run_all.py --ui                      # start Streamlit UI (background) and save pid
  python run_all.py --cleanup                 # cleanup demo artifacts (temp files + startup entry)
  python run_all.py --stop-ui                 # stop background Streamlit UI started by this script
"""

import argparse
import subprocess
import sys
import os
import time
import glob
import tempfile
import platform
from pathlib import Path

PY = sys.executable
ROOT = Path(__file__).resolve().parent

PID_FILE = ROOT / ".streamlit_pid"

def run_cmd(cmd, check=True):
    print(f"[+] Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=ROOT)
    if check and res.returncode != 0:
        print(f"[!] Command returned non-zero exit code: {res.returncode}")
    return res.returncode

def python_script(script_name, args=None):
    script = ROOT / script_name
    if not script.exists():
        print(f"[!] Script not found: {script_name}")
        return 1
    cmd = [PY, str(script)]
    if args:
        cmd += args
    return run_cmd(cmd)

def start_streamlit():
    # start streamlit in background, save PID so we can stop it later
    ui_script = ROOT / "scripts" / "ui_streamlit.py"
    if not ui_script.exists():
        print(f"[!] UI script not found: {ui_script}")
    cmd = [PY, "-m", "streamlit", "run", str(ui_script), "--server.headless=true"]
    print("[+] Starting Streamlit UI in background...")
    p = subprocess.Popen(cmd, cwd=ROOT)
    pid = p.pid
    print(f"[+] Streamlit started with PID {pid}. Open your browser at URL: http://localhost:8501 (or other port)")
    with open(PID_FILE, "w") as f:  #save PID so that we can stop it later
        f.write(str(pid))
    # give it a second to start
    time.sleep(2)
    return pid

def stop_streamlit():
    if not PID_FILE.exists():
        print("[!] No PID file found for Streamlit. Maybe it wasn't started by this script.")
        return
    pid = int(PID_FILE.read_text().strip())
    print(f"[+] Stopping Streamlit PID {pid} ...")
    try:
        if platform.system() == "Windows":
            run_cmd(["taskkill", "/PID", str(pid), "/F"], check=False)
        else:
            run_cmd(["kill", str(pid)], check=False)
        PID_FILE.unlink(missing_ok=True)
        print("[+] Streamlit stopped.")
    except Exception as e:
        print("[!] Failed to stop Streamlit:", e)

def cleanup_demo_artifacts():
    # Remove temp files created by simulate_suspicious.py
    temp = tempfile.gettempdir()
    removed = 0
    for i in range(50):  # try a bunch just in case
        p = os.path.join(temp, f"dummy_temp_file_{i}.txt")
        if os.path.exists(p):
            try:
                os.remove(p)
                removed += 1
            except Exception:
                pass
    print(f"[+] Removed {removed} dummy temp files from {temp}")

    # Remove startup entry depending on OS
    os_type = platform.system()
    if os_type == "Windows":
        startup = os.path.join(os.environ.get("APPDATA",""), r"Microsoft\Windows\Start Menu\Programs\Startup", "dummy-demo.bat")
        if os.path.exists(startup):
            try:
                os.remove(startup)
                print(f"[+] Removed Windows startup entry: {startup}")
            except Exception as e:
                print("[!] Could not remove startup entry:", e)
    elif os_type == "Linux":
        autostart = os.path.expanduser("~/.config/autostart/dummy-demo.desktop")
        if os.path.exists(autostart):
            try:
                os.remove(autostart)
                print(f"[+] Removed Linux autostart entry: {autostart}")
            except Exception as e:
                print("[!] Could not remove autostart entry:", e)
    else:
        print("[!] Unknown OS: skipping startup cleanup")

def main():
    parser = argparse.ArgumentParser(description="Orchestrate Keylogger Detector scripts (student-friendly).")
    parser.add_argument("--collect", action="store_true", help="Run collector.py")
    parser.add_argument("--synth", action="store_true", help="Run synth_data.py")
    parser.add_argument("--train", action="store_true", help="Run train_model.py")
    parser.add_argument("--detect", action="store_true", help="Run detector_live.py")
    parser.add_argument("--simulate", action="store_true", help="Run demo_scripts/simulate_suspicious.py (VM only)")
    parser.add_argument("--ui", action="store_true", help="Start Streamlit UI in background")
    parser.add_argument("--stop-ui", action="store_true", help="Stop Streamlit UI started by this script")
    parser.add_argument("--cleanup", action="store_true", help="Remove demo artifacts (temp files + startup entry)")
    parser.add_argument("--all", action="store_true", help="Run collect -> synth -> train -> detect in sequence")
    args = parser.parse_args()

    if args.all:
        steps = ["collect", "synth", "train", "detect"]
    else:
        steps = []
        if args.collect: steps.append("collect")
        if args.synth: steps.append("synth")
        if args.train: steps.append("train")
        if args.detect: steps.append("detect")

    # run requested steps
    for step in steps:
        if step == "collect":
            python_script("scripts/collector.py")
        elif step == "synth":
            python_script("scripts/synth_data.py")
        elif step == "train":
            python_script("scripts/train_model.py")
        elif step == "detect":
            python_script("scripts/detector_live.py")

    if args.simulate:
        print("[!] Running simulate_suspicious.py (make sure you are in a VM!)")
        python_script(os.path.join("demo_scripts", "simulate_suspicious.py"))

    if args.ui:
        start_streamlit()

    if args.stop_ui or args.stop_ui:  # alias
        stop_streamlit()

    if args.cleanup:
        cleanup_demo_artifacts()

if __name__ == "__main__":
    main()


'''Notes:
 - Run this from project root inside your venv.
 - It will use the same python interpreter used to run this script.
 - UI is launched in the background; PID saved to `.streamlit_pid`.
 - Cleanup only removes demo-generated files created by simulate_suspicious.py'''