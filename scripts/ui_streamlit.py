# ui_streamlit.py
import streamlit as st
import pandas as pd
from detector_live import score_snapshot

st.title("Keylogger Detector — Telemetry & Scores")

df, suspicious = score_snapshot()
st.subheader("Top Suspicious Processes")
st.write(suspicious.filter(
    items=["pid","name","score","open_files","connections","in_startup","path_in_temp"], axis=1).reset_index(drop=True))

st.subheader("All Processes (scored)")
st.dataframe(df[["pid","name","score","open_files","connections","in_startup","path_in_temp"]].sort_values("score", ascending=False))

# optional footer
st.markdown("---")
st.markdown("**Author:** Kritika Sharma")
st.caption("Made by Kritika — © 2025")
