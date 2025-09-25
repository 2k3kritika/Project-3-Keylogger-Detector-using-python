## Keylogger Detector (student prototype)

This project collects non-sensitive telemetry from running processes and uses a RandomForest to flag suspicious processes that show behavior similar to keyloggers (e.g., many open files, network connections, startup persistence). It never captures keyboard input.

Usage:
1. Create a venv and install requirements: `pip install -r requirements.txt`
2. Take snapshot: `python collector.py`
3. Build dataset: `python synth_data.py`
4. Train model: `python train_model.py`
5. Run detector: `python detector_live.py`
6. Run demo script in another terminal: `python demo_scripts/simulate_suspicious.py`
7. Start UI: `streamlit run ui_streamlit.py`

Test only in a VM. See report.md for limitations and ethics.

Setup:(one time)
`python -m venv venv`   #create a VM
`.\venv\Scripts\Activate.ps1`   #activates the VM
`python -m pip install --upgrade pip` # upgrade the pip to the latest version
`pip install -r requirements.txt`   #install all required modules in VM
`Remove-Item -Recurse -Force .\venv`    #to delete this current vm in powershell
`rmdir /s /q venv`  #to delete the vm using cmd

---------------------Running the detector-----------------------
Steps to run the whole detector:
1. take a telemetry snapshot
`python collector.py`
print a table and saves telemetry_snapshot.csv
2. build data set
`python synth_data.py`
creates dataset.csv (benign rows + synthetic suspicious rows)
3. train the model
`python train_model.py`
prints classification report and saves model.pkl
4. run the live detector
`python detector_live.py`
prints suspicious processes (score >= threshold) and saves live_snapshot_score.csv
5. start streamlit UI
`streamlit run ui_streamlit.py`
open http://localhost.8501
6. DEMO: simulating suspicious behaviour in vm; in another terminal
`python C:\Users\FSPIT\Documents\project_3_keylogger_detector\demo_scripts\simulate_suspicious.py`

then re-run `python detector_live.py` this time detector will show flagging simulated activity.

-------------------To check either our fake keylogger simulate_suspicious.py is actually closed or not----------
1. Check Python processes in Task Manager (Windows)

Press `Ctrl + Shift + Esc` → open Task Manager.

Look under the Processes tab.
Find any Python or python.exe entries.
If your simulation is stopped, no extra Python processes should appear besides ones you intentionally ran.
If you see a leftover one, right-click → End Task.

2. Check via Command Line / PowerShell
PowerShell
`Get-Process python*`

Lists all running Python processes.
If nothing shows, your simulation isn’t running.

If you see a PID, you can stop it:
`Stop-Process -Id <PID>`

CMD
`tasklist | findstr python`
Same idea — no output = nothing running.

Kill process if needed:
`taskkill /PID <PID> /F`

3. Check your simulated network connections
If your simulate_suspicious.py opened fake network sockets, you can verify they’re closed:
PowerShell
`netstat -ano | findstr 5000`

5000 is the port used in the simulation script.
No output → no leftover sockets.

4. Check startup entries
Make sure the dummy startup file isn’t still there:

Windows
`Test-Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\dummy-demo.bat"`
Returns False → nothing running at startup.

Delete if needed:
`Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\dummy-demo.bat"`

✅ Quick Checklist
Task Manager → no Python processes.
Startup folder → dummy file deleted.
Network ports → no leftover demo connections.
Temp files → optionally delete after demo.
If all four are clear, your simulated keylogger activity is completely stopped.

---------------this is all about this project---------------------------
