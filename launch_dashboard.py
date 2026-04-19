import subprocess
import sys

# Run streamlit directly
subprocess.run([
    sys.executable, "-m", "streamlit", "run",
    "src/dashboard/app.py",
    "--server.port", "8501",
    "--server.address", "0.0.0.0"
])
