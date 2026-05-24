"""Interactive notebook wrappers (07_interactive_dashboard.ipynb)
Contains small helpers to provide structured payloads for interactive components.
"""

def load_interactive_state():
    return {'patient_id': 'PT_001', 'weeks': 32, 'auto_fetch': False}


def run():
    return load_interactive_state()
