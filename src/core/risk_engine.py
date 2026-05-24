def classify_risk(score: float) -> str:
    if score >= 80:
        return "REJECT"
    elif score >= 50:
        return "WARN"
    return "ACCEPT"


def developmental_index(
    growth: float,
    oxygen: float,
    movement: float,
    maternal_stability: float,
) -> float:
    total = (
        growth * 0.3
        + oxygen * 0.3
        + movement * 0.2
        + maternal_stability * 0.2
    )
    return max(0.0, min(100.0, total))
