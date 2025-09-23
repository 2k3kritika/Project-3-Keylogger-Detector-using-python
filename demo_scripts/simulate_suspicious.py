import os
import tempfile
import socket
import time
import platform

# ---------- 1. Create temp files to simulate unusual file activity ----------
def create_temp_files(n=5):
    temp_dir = tempfile.gettempdir()
    created_files = []
    for i in range(n):
        file_path = os.path.join(temp_dir, f"dummy_temp_file_{i}.txt")
        with open(file_path, "w") as f:
            f.write("This is a dummy file to simulate suspicious behavior.\n")
        created_files.append(file_path)
    print(f"[+] Created {n} temp files in {temp_dir}")
    return created_files

# ---------- 2. Open dummy network connections ----------
def simulate_network_connections(n=2):
    connections = []
    for i in range(n):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            # Connect to localhost: random high ports (won't actually harm)
            s.connect(("127.0.0.1", 5000 + i))
            connections.append(s)
        except Exception:
            pass
    print(f"[+] Simulated {n} network connection attempts (harmless)")
    return connections

# ---------- 3. Optional: create startup entry ----------
def create_startup_entry():
    os_type = platform.system()
    if os_type == "Linux":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        dummy_file = os.path.join(autostart_dir, "dummy-demo.desktop")
        with open(dummy_file, "w") as f:
            f.write("[Desktop Entry]\nType=Application\nName=DummyDemo\nExec=python3 simulate_suspicious.py\n")
        print(f"[+] Created dummy startup entry (Linux) at {dummy_file}")
    elif os_type == "Windows":
        startup_dir = os.path.join(os.environ['APPDATA'], r"Microsoft\Windows\Start Menu\Programs\Startup")
        dummy_file = os.path.join(startup_dir, "dummy-demo.bat")
        with open(dummy_file, "w") as f:
            f.write("@echo off\n")
            f.write("echo Dummy Demo Script\n")
        print(f"[+] Created dummy startup entry (Windows) at {dummy_file}")
    else:
        print("[!] Unknown OS — skipping startup entry")

# ---------- Main simulation ----------
if __name__ == "__main__":
    print("[*] Starting suspicious activity simulation...")
    temp_files = create_temp_files()
    conns = simulate_network_connections()
    create_startup_entry()
    
    print("[*] Simulation running for 5 seconds...")
    time.sleep(5)

    # Cleanup network connections
    for s in conns:
        s.close()

    print("[+] Simulation complete. Temp files remain for detector to flag them.")
