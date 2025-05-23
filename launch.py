import os
import subprocess

# Safely remove invalid env var injected by Railway
if "STREAMLIT_SERVER_PORT" in os.environ:
    del os.environ["STREAMLIT_SERVER_PORT"]

# Get real port from Railway's $PORT
port = os.environ.get("PORT", "8501")

# Run Streamlit as a subprocess
subprocess.run([
    "streamlit",
    "run",
    "streamlit_ui.py",
    "--server.port", str(port),
    "--server.enableCORS", "false",
    "--server.enableXsrfProtection", "false"
])
