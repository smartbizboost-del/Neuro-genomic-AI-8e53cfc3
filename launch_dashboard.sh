#!/bin/bash
cd /workspaces/Neuro-genomic-AI
export PYTHONPATH=/workspaces/Neuro-genomic-AI:$PYTHONPATH
export API_URL=http://localhost:8000

# Run streamlit with the correct path
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
