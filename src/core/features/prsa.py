# src/core/features/prsa.py
import numpy as np


def phase_rectified_signal_averaging(rr_intervals, T=9):
    """
    Compute Acceleration Capacity (AC) and Deceleration Capacity (DC)
    using Phase-Rectified Signal Averaging.

    Parameters:
    -----------
    rr_intervals : array-like
        RR intervals in milliseconds
    T : int
        Time window parameter (T=9 is optimal for IUGR detection)

    Returns:
    --------
    dict : {'AC': float, 'DC': float}
    """
    rr = np.array(rr_intervals)
    N = len(rr)

    # Compute anchor points where RR increases (for AC) or decreases (for DC)
    increases = np.where(np.diff(rr) > 0)[0]
    decreases = np.where(np.diff(rr) < 0)[0]

    # For each anchor, take window [-T, T] and average
    def average_window(anchors, rr, T):
        windows = []
        for anchor in anchors:
            if anchor - T >= 0 and anchor + T < len(rr):
                window = rr[anchor - T:anchor + T + 1]
                windows.append(window)
        if not windows:
            return np.nan
        return np.mean(np.array(windows), axis=0)

    ac_signal = average_window(increases, rr, T)
    dc_signal = average_window(decreases, rr, T)

    # AC and DC are the average of the window
    ac = np.mean(ac_signal) if ac_signal is not np.nan else np.nan
    dc = np.mean(dc_signal) if dc_signal is not np.nan else np.nan

    return {'AC_T9': ac, 'DC_T9': dc}
