
# Define severity levels for new resource access
RISK_LEVELS = {
    "public": {
        "read": "low",
        "write": "medium"
    },
    "internal": {
        "read": "low",
        "write": "medium"
    },
    "confidential": {
        "read": "high",
        "write": "high"
    },
    "restricted": {
        "read": "high",
        "write": "critical"
    }
}


# Evaluate the severity of newly granted access
def evaluate_risk(finding):

    sensitivity = finding["sensitivity"]
    action = finding["action"]

    # Look up the severity based on sensitivity and action
    severity = RISK_LEVELS[sensitivity][action]

    # Copy the original finding to preserve its information
    result = finding.copy()

    # Add the severity and explanation to the finding
    result["severity"] = severity
    result["reason"] = f"New {action} access to a {sensitivity} resource"

    return result


# Get the severity value used for sorting
def get_severity_value(finding):

    severity_order = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }

    return severity_order[finding["severity"]]


# Analyze and sort security findings from a simulation
def analyze_simulation(simulation_result):

    findings = []

    # Evaluate each newly accessible resource
    for access in simulation_result["new_access"]:
        risk = evaluate_risk(access)
        findings.append(risk)

    # Sort findings from highest to lowest severity
    findings.sort(key=get_severity_value, reverse=True)

    return findings
