"""
Reliable Suspicious Activity Simulator for Keylogger Detector

This script creates a long-running "suspicious" process so that
detector_live.py can detect it. It:
 - creates temp files (dummy_temp_file_*.txt)
 - launches a background child process with 'keylogger' in its filename or cmdline
 - child process keeps a temp file open and a socket open
 - writes a harmless startup entry (Windows/Linux)
"""

import os
import tempfile
import subprocess
import sys
import time
import platform
import shutil

# ----------------- Create temp files -----------------
def create_temp_files(n=3):
    temp_dir = tempfile.gettempdir()
    created = []
    for i in range(n):
        p = os.path.join(temp_dir, f"dummy_temp_file_{i}.txt")
        with open(p, "w") as f:
            f.write("This is a dummy file to simulate suspicious behavior.\n")
        created.append(p)
    print(f"[+] Created {len(created)} temp files in {temp_dir}")
    return created

# ----------------- Child process -----------------
def write_long_running_child(sleep_seconds=60):
    """Create a child process that looks suspicious to the detector"""
    temp_dir = tempfile.gettempdir()
    child_name = "keylogger_fake_child.py"
    child_path = os.path.join(temp_dir, child_name)

    # Child script content
    child_code = f"""
import time, tempfile, socket, os, sys

# Keep a temp file open
file_path = os.path.join(tempfile.gettempdir(), "dummy_temp_file_child.txt")
f = open(file_path, "a+")
f.write("child process holding file open for simulation\\n")
f.flush()

# Open a dummy network socket to be detected
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(("127.0.0.1", 0))  # bind to any free port
    s.listen(1)
except:
    s = None

# Sleep for the given duration
time.sleep({sleep_seconds})

# Cleanup
try:
    if s:
        s.close()
    f.close()
except:
    pass
"""

    # Write child script to temp
    with open(child_path, "w", encoding="utf-8") as f:
        f.write(child_code)

    # Launch child detached and pass 'keylogger' argument to trigger cmdline detection
    cmd = [sys.executable, child_path, "keylogger"]
    if platform.system() == "Windows":
        DETACHED = 0x00000008
        p = subprocess.Popen(cmd, creationflags=DETACHED, cwd=temp_dir)
    else:
        p = subprocess.Popen(cmd, start_new_session=True, cwd=temp_dir)

    print(f"[+] Launched child process: {child_path} PID={p.pid}")
    return p.pid

# ----------------- Optional startup entry -----------------
def create_startup_entry():
    os_type = platform.system()
    if os_type == "Linux":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        dummy_file = os.path.join(autostart_dir, "dummy-demo.desktop")
        with open(dummy_file, "w") as f:
            f.write("[Desktop Entry]\nType=Application\nName=DummyDemo\nExec=python3 simulate_suspicious.py keylogger\n")
        print(f"[+] Created dummy startup entry (Linux) at {dummy_file}")
    elif os_type == "Windows":
        try:
            startup_dir = os.path.join(os.environ['APPDATA'], r"Microsoft\Windows\Start Menu\Programs\Startup")
            os.makedirs(startup_dir, exist_ok=True)
            # Copy the script itself into startup folder to trigger in_startup
            startup_script = os.path.join(startup_dir, "keylogger_fake_child_startup.py")
            shutil.copy2(os.path.join(tempfile.gettempdir(), "keylogger_fake_child.py"), startup_script)
            print(f"[+] Copied child script into Windows startup folder: {startup_script}")
        except Exception as e:
            print("[!] Could not create startup entry:", e)
    else:
        print("[!] Unknown OS — skipping startup entry")

# ----------------- Main -----------------
if __name__ == "__main__":
    print("[*] Starting reliable suspicious activity simulation...")
    create_temp_files(3)
    child_pid = write_long_running_child(sleep_seconds=120)  # long enough to run detector
    create_startup_entry()

    print("[*] Simulation running. Child PID:", child_pid)
    print("[*] You can now run the detector or run --simulate --detect.")
