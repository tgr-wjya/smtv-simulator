import json
import pytest
import tempfile
import os
from src.runner import load_config


def test_load_config_creates_temp_file():
    """Test load_config reads temp config file successfully"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            "attacker": {
                "name": "Nahobino",
                "stats": {"STR": 45, "VIT": 38, "MAG": 42, "AGI": 40, "LUC": 35}
            },
            "defender": {
                "name": "Daemon",
                "stats": {"STR": 50, "VIT": 55, "MAG": 40, "AGI": 35, "LUC": 30}
            },
            "scenarios": [
                {
                    "name": "No buffs",
                    "attacker_buffs": {},
                    "defender_buffs": {}
                }
            ],
            "formulas": {
                "weakness_multiplier": 1.5,
                "crit_multiplier": 1.5,
                "skill_power": 100
            }
        }
        json.dump(config_data, f)
        temp_file = f.name

    try:
        loaded = load_config(temp_file)
        assert loaded is not None
    finally:
        os.unlink(temp_file)


def test_load_config_parses_attacker_section():
    """Test load_config correctly parses attacker section"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            "attacker": {
                "name": "TestAttacker",
                "stats": {"STR": 45, "VIT": 38, "MAG": 42, "AGI": 40, "LUC": 35}
            },
            "defender": {
                "name": "TestDefender",
                "stats": {"STR": 50, "VIT": 55, "MAG": 40, "AGI": 35, "LUC": 30}
            },
            "scenarios": [],
            "formulas": {
                "weakness_multiplier": 1.5,
                "crit_multiplier": 1.5,
                "skill_power": 100
            }
        }
        json.dump(config_data, f)
        temp_file = f.name

    try:
        loaded = load_config(temp_file)
        assert loaded["attacker"]["name"] == "TestAttacker"
        assert loaded["attacker"]["stats"]["STR"] == 45
        assert loaded["attacker"]["stats"]["VIT"] == 38
    finally:
        os.unlink(temp_file)


def test_load_config_parses_defender_section():
    """Test load_config correctly parses defender section"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            "attacker": {
                "name": "TestAttacker",
                "stats": {"STR": 45, "VIT": 38, "MAG": 42, "AGI": 40, "LUC": 35}
            },
            "defender": {
                "name": "TestDefender",
                "stats": {"STR": 50, "VIT": 55, "MAG": 40, "AGI": 35, "LUC": 30}
            },
            "scenarios": [],
            "formulas": {
                "weakness_multiplier": 1.5,
                "crit_multiplier": 1.5,
                "skill_power": 100
            }
        }
        json.dump(config_data, f)
        temp_file = f.name

    try:
        loaded = load_config(temp_file)
        assert loaded["defender"]["name"] == "TestDefender"
        assert loaded["defender"]["stats"]["STR"] == 50
        assert loaded["defender"]["stats"]["VIT"] == 55
    finally:
        os.unlink(temp_file)


def test_load_config_parses_scenarios_section():
    """Test load_config correctly parses scenarios section"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            "attacker": {
                "name": "TestAttacker",
                "stats": {"STR": 45, "VIT": 38, "MAG": 42, "AGI": 40, "LUC": 35}
            },
            "defender": {
                "name": "TestDefender",
                "stats": {"STR": 50, "VIT": 55, "MAG": 40, "AGI": 35, "LUC": 30}
            },
            "scenarios": [
                {
                    "name": "Scenario 1",
                    "attacker_buffs": {"STR": 3},
                    "defender_buffs": {}
                },
                {
                    "name": "Scenario 2",
                    "attacker_buffs": {},
                    "defender_buffs": {"VIT": -2}
                }
            ],
            "formulas": {
                "weakness_multiplier": 1.5,
                "crit_multiplier": 1.5,
                "skill_power": 100
            }
        }
        json.dump(config_data, f)
        temp_file = f.name

    try:
        loaded = load_config(temp_file)
        assert len(loaded["scenarios"]) == 2
        assert loaded["scenarios"][0]["name"] == "Scenario 1"
        assert loaded["scenarios"][0]["attacker_buffs"]["STR"] == 3
        assert loaded["scenarios"][1]["name"] == "Scenario 2"
        assert loaded["scenarios"][1]["defender_buffs"]["VIT"] == -2
    finally:
        os.unlink(temp_file)


def test_load_config_parses_formulas_section():
    """Test load_config correctly parses formulas section"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            "attacker": {
                "name": "TestAttacker",
                "stats": {"STR": 45, "VIT": 38, "MAG": 42, "AGI": 40, "LUC": 35}
            },
            "defender": {
                "name": "TestDefender",
                "stats": {"STR": 50, "VIT": 55, "MAG": 40, "AGI": 35, "LUC": 30}
            },
            "scenarios": [],
            "formulas": {
                "weakness_multiplier": 2.0,
                "crit_multiplier": 1.75,
                "skill_power": 125
            }
        }
        json.dump(config_data, f)
        temp_file = f.name

    try:
        loaded = load_config(temp_file)
        assert loaded["formulas"]["weakness_multiplier"] == 2.0
        assert loaded["formulas"]["crit_multiplier"] == 1.75
        assert loaded["formulas"]["skill_power"] == 125
    finally:
        os.unlink(temp_file)


def test_load_config_file_not_found():
    """Test load_config raises error if file doesn't exist"""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.json")


def test_load_config_invalid_json():
    """Test load_config raises error on invalid JSON"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        temp_file = f.name

    try:
        with pytest.raises(json.JSONDecodeError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)
