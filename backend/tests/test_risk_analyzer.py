
from app.core.risk_analyzer import (
    evaluate_risk,
    analyze_simulation
)


# Check risk classification for restricted write access
def test_critical_risk():
    finding = {
        "resource": "private_db",
        "action": "write",
        "sensitivity": "restricted",
        "path": ["agent", "db_tool", "private_db"]
    }

    result = evaluate_risk(finding)

    assert result["severity"] == "critical"


# Check risk classification for public read access
def test_low_risk():
    finding = {
        "resource": "public_files",
        "action": "read",
        "sensitivity": "public",
        "path": ["agent", "file_tool", "public_files"]
    }

    result = evaluate_risk(finding)

    assert result["severity"] == "low"


# Check that findings are sorted by severity
def test_risk_sorting():
    simulation = {
        "new_access": [
            {
                "resource": "public_files",
                "action": "read",
                "sensitivity": "public",
                "path": ["agent", "tool", "public_files"]
            },
            {
                "resource": "private_db",
                "action": "write",
                "sensitivity": "restricted",
                "path": ["agent", "tool", "private_db"]
            }
        ]
    }

    findings = analyze_simulation(simulation)

    assert findings[0]["severity"] == "critical"
    assert findings[1]["severity"] == "low"


# Check simulations without new access
def test_no_new_risks():
    simulation = {"new_access": []}

    assert analyze_simulation(simulation) == []
