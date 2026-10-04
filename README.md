# Keylogger Detector

This project collects non-sensitive telemetry from running processes and uses a RandomForest to flag suspicious processes that show behavior similar to keyloggers (e.g., many open files, network connections, startup persistence). It never captures keyboard input.

---

## Usage

1. Create a venv and install requirements:
   `pip install -r requirements.txt`

2. Take snapshot:
   `python collector.py`

3. Build dataset:
   `python synth_data.py`

4. Train model:
   `python train_model.py`

5. Run detector:
   `python detector_live.py`

6. Run demo script in another terminal:
   `python demo_scripts/simulate_suspicious.py`

7. Start UI:
   `streamlit run ui_streamlit.py`

**Test only in a VM. See `report.md` for limitations and ethics.**

---

## run_all.py

This script controls all the required scripts for the Keylogger Detector project.

### Usage

```bash
python run_all.py --all                     # run collect -> synth -> train -> detect
python run_all.py --collect                 # only run collector.py
python run_all.py --simulate --detect       # run demo simulate then run detector
python run_all.py --ui                      # start Streamlit UI (background) and save pid
python run_all.py --cleanup                 # cleanup demo artifacts (temp files + startup entry)
python run_all.py --stop-ui                 # stop background Streamlit UI started by this script
```

---

## Setup: One-Time Virtual Environment

```powershell
python -m venv venv
```

Create a virtual environment.

```powershell
.\venv\Scripts\Activate.ps1
```

Activate the virtual environment.

```powershell
python -m pip install --upgrade pip
```

Upgrade pip to the latest version.

```powershell
pip install -r requirements.txt
```

Install all required modules in the virtual environment.

### Delete the Virtual Environment

PowerShell:

```powershell
Remove-Item -Recurse -Force .\venv
```

CMD:

```cmd
rmdir /s /q venv
```

Deactivate the current virtual environment:

```powershell
deactivate
```

---

## Running the Detector

### 1. Take a Telemetry Snapshot

```bash
python collector.py
```

Telemetry data is collected and stored locally as CSV/JSON. Due to privacy and size concerns, full raw logs are not uploaded. A sample snapshot is included for reference.

Prints a table and saves:

```text
telemetry_snapshot.csv
```

---

### 2. Build Dataset

```bash
python synth_data.py
```

Creates:

```text
dataset.csv
```

The dataset contains benign rows and synthetic suspicious rows.

---

### 3. Train the Model

```bash
python train_model.py
```

Prints a classification report and saves:

```text
model.pkl
```

---

### 4. Run the Live Detector

```bash
python detector_live.py
```

Prints suspicious processes (score >= threshold) and saves:

```text
live_snapshot_score.csv
```

---

### 5. Start Streamlit UI

```bash
streamlit run ui_streamlit.py
```

Open:

```text
http://localhost.8501
```

---

### 6. Demo: Simulating Suspicious Behaviour in a VM

In another terminal:

```bash
python simulate_suspicious.py
```

Then re-run:

```bash
python detector_live.py
```

This time, the detector will show flagging simulated activity.

---

## Checking Whether `simulate_suspicious.py` Is Actually Closed

### 1. Check Python Processes in Task Manager (Windows)

Press:

`Ctrl + Shift + Esc`

Open **Task Manager**.

Look under the **Processes** tab.

Find any `Python` or `python.exe` entries.

If your simulation is stopped, no extra Python processes should appear besides ones you intentionally ran.

If you see a leftover one:

**Right-click → End Task**

---

### 2. Check via Command Line / PowerShell

#### PowerShell

```powershell
Get-Process python*
```

Lists all running Python processes.

If nothing shows, your simulation isn't running.

If you see a PID, you can stop it:

```powershell
Stop-Process -Id <PID>
```

#### CMD

```cmd
tasklist | findstr python
```

Same idea: no output means nothing is running.

Kill the process if needed:

```cmd
taskkill /PID <PID> /F
```

---

### 3. Check Simulated Network Connections

If your `simulate_suspicious.py` opened fake network sockets, you can verify they're closed.

#### PowerShell

```powershell
netstat -ano | findstr 5000
```

`5000` is the port used in the simulation script.

**No output → no leftover sockets.**

---

### 4. Check Startup Entries

Make sure the dummy startup file isn't still there.

#### Windows

```powershell
Test-Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\dummy-demo.bat"
```

Returns:

```text
False
```

→ Nothing is running at startup.

Delete it if needed:

```powershell
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\dummy-demo.bat"
```

---

## ✅ Quick Checklist for Cleanup

- **Task Manager** → No Python processes.
- **Startup folder** → Dummy file deleted.
- **Network ports** → No leftover demo connections.
- **Temp files** → Optionally delete after demo.

If all four are clear, your simulated keylogger activity is completely stopped.

---

## Project Overview

This README contains the setup, usage, detector workflow, `run_all.py` commands, demo instructions, and cleanup steps for the **Keylogger Detector** project.
```
