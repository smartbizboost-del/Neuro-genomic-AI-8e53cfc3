REQUIRED_FIELDS = [
    "blood_pressure",
    "fetal_heart_rate",
    "gestational_age",
    "oxygen_saturation",
]


def validate_inputs(data):
    missing = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            missing.append(field)

    return {
        "valid": len(missing) == 0,
        "missing_fields": missing,
    }
