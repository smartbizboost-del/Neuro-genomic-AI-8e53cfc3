#!/usr/bin/env python3
"""Wrapper script to run Streamlit from project root."""

import sys
import os

# Ensure project root is in Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Change to project root
os.chdir(project_root)

# Import and run Streamlit
if __name__ == "__main__":
    import streamlit.cli
    sys.argv = ["streamlit", "run", "src/dashboard/app.py", "--logger.level=debug"]
    streamlit.cli.main()
