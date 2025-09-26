#!/usr/bin/env python3
"""
Aggressive Suspicious Activity Simulator for Keylogger Detector

- Holds many open files (50)
- Opens multiple listening sockets (up to 10)
- Launches a detached child process with suspicious argv keywords:
    "keylogger", "hook", "capture", "keyboard", "autostart", "stealth"
- Registers cleanup via atexit
- Attempts to create a harmless startup entry (Linux .desktop or copy to Windows Startup)
- Intended to be run in a VM for demos/tests only.
"""

import os
import tempfile
import subprocess
import sys
import time
import platform
import shutil

# ----------------- Create temp files -----------------
def create_temp_files(n=10):
    temp_dir = tempfile.gettempdir()
    created = []
    for i in range(n):
        p = os.path.join(temp_dir, f"dummy_temp_file_{i}.txt")
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write("This is a dummy file to simulate suspicious behavior.\n")
            created.append(p)
        except Exception:
            pass
    print(f"[+] Created {len(created)} temp files in {temp_dir}")
    return created

# ----------------- Child process writer -----------------
def write_long_running_child(sleep_seconds=300):
    """
    Create a child script in temp that:
     - holds many files open
     - opens multiple listening sockets (tries up to 10)
     - sleeps for sleep_seconds
    Launch it detached with suspicious cmdline args.
    """
    temp_dir = tempfile.gettempdir()
    child_name = "keylogger_fake_child.py"
    child_path = os.path.join(temp_dir, child_name)

    child_code = f'''import time, tempfile, socket, os, sys, atexit

open_files = []
try:
    # Hold many temp files open to increase open_files count reported by psutil
    for i in range(50):  # 50 files
        try:
            fp = os.path.join(tempfile.gettempdir(), "child_hold_file_{{}}.tmp".format(i))
            fh = open(fp, "a+", encoding="utf-8")
            fh.write("child holding file open for simulation\\n")
            fh.flush()
            open_files.append(fh)
        except Exception:
            pass
except Exception:
    pass

sockets = []
try:
    # Try to open multiple listening sockets so netstat/psutil shows connections
    for i in range(10):  # try up to 10 sockets
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # attempt to bind to successive ports starting at 5000, fallback to 0 if in use
            port = 5000 + i
            try:
                s.bind(("127.0.0.1", port))
                s.listen(1)
                sockets.append(s)
            except Exception:
                try:
                    s.bind(("127.0.0.1", 0))
                    s.listen(1)
                    sockets.append(s)
                except Exception:
                    s.close()
        except Exception:
            pass
except Exception:
    pass

def cleanup():
    try:
        for s in sockets:
            try:
                s.close()
            except:
                pass
    except:
        pass
    try:
        for f in open_files:
            try:
                f.close()
            except:
                pass
    except:
        pass

atexit.register(cleanup)

# keep running long enough for detector to inspect the process
time.sleep({sleep_seconds})
'''

    # Write child script to temp
    try:
        with open(child_path, "w", encoding="utf-8") as f:
            f.write(child_code)
        try:
            os.chmod(child_path, 0o700)
        except Exception:
            pass
    except Exception as e:
        print("[!] Could not write child script:", e)
        return None

    # Launch child detached and pass multiple suspicious keywords to trigger cmdline detection
    cmd = [sys.executable, child_path, "keylogger", "hook", "capture", "keyboard", "autostart", "stealth"]
    try:
        if platform.system() == "Windows":
            # DETACHED_PROCESS
            DETACHED = 0x00000008
            p = subprocess.Popen(cmd, creationflags=DETACHED, cwd=temp_dir, close_fds=True)
        else:
            p = subprocess.Popen(cmd, start_new_session=True, cwd=temp_dir, close_fds=True)
    except Exception as e:
        print("[!] Failed to launch child process:", e)
        return None

    print(f"[+] Launched child process: {child_path} PID={p.pid}")
    return p.pid

# ----------------- Optional startup entry -----------------
def create_startup_entry():
    os_type = platform.system()
    if os_type == "Linux":
        try:
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            child_temp = os.path.join(tempfile.gettempdir(), "keylogger_fake_child.py")
            dummy_file = os.path.join(autostart_dir, "dummy-demo.desktop")
            with open(dummy_file, "w", encoding="utf-8") as f:
                f.write("[Desktop Entry]\\nType=Application\\nName=DummyDemo\\nExec=python3 " + child_temp + " keylogger\\n")
            print(f"[+] Created dummy startup entry (Linux) at {dummy_file}")
        except Exception as e:
            print("[!] Could not create Linux autostart entry:", e)
    elif os_type == "Windows":
        try:
            startup_dir = os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            os.makedirs(startup_dir, exist_ok=True)
            src = os.path.join(tempfile.gettempdir(), "keylogger_fake_child.py")
            startup_script = os.path.join(startup_dir, "keylogger_fake_child_startup.py")
            if os.path.exists(src):
                shutil.copy2(src, startup_script)
                print(f"[+] Copied child script into Windows startup folder: {startup_script}")
            else:
                # write a small stub that will run the temp child on login
                stub_path = os.path.join(startup_dir, "keylogger_fake_child_startup.py")
                try:
                    with open(stub_path, "w", encoding="utf-8") as f:
                        f.write("import os, tempfile, sys, subprocess\\nchild = os.path.join(tempfile.gettempdir(), 'keylogger_fake_child.py')\\nsubprocess.Popen([sys.executable, child, 'keylogger'])\\n")
                    print(f"[+] Wrote stub startup script: {stub_path}")
                except Exception as e:
                    print("[!] Could not write stub startup script:", e)
        except Exception as e:
            print("[!] Could not create Windows startup entry:", e)
    else:
        print("[!] Unknown OS — skipping startup entry")

# ----------------- Main -----------------
if __name__ == "__main__":
    print("[*] Starting aggressive suspicious activity simulation (DEMO ONLY)...")
    create_temp_files(10)
    child_pid = write_long_running_child(sleep_seconds=300)
    create_startup_entry()
    print("[*] Simulation running. Child PID:", child_pid)
    print("[*] Now run `python detector_live.py` in another terminal to test detection.")
