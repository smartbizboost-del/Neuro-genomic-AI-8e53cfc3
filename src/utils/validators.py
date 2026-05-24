"""
Data validation utilities
"""

import os
from typing import List

ALLOWED_EXTENSIONS = ['.csv', '.txt', '.edf', '.hea', '.dat']


def validate_file_extension(filename: str) -> bool:
    """Validate file extension"""
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


def validate_file_size(file_size: int,
                       max_size: int = 100 * 1024 * 1024) -> bool:
    """Validate file size (default 100MB)"""
    return file_size <= max_size


def validate_gestational_weeks(weeks: int) -> bool:
    """Validate gestational weeks (20-42 weeks)"""
    return 20 <= weeks <= 42


def validate_rr_intervals(rr_intervals: List[float]) -> bool:
    """Validate RR intervals (basic checks)"""
    if not rr_intervals:
        return False

    # Check for reasonable RR interval ranges (300-2000ms)
    return all(300 <= rr <= 2000 for rr in rr_intervals)
