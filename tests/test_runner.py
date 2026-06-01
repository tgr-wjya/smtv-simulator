import json
import pytest
import tempfile
import os
from io import StringIO
import sys
from src.runner import load_config, run_scenario, run_all_scenarios, print_table
from src.combat_engine import CombatEngine, Combatant


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


def test_run_scenario_no_buffs():
    """Test run_scenario with baseline (no buffs)"""
    engine = CombatEngine(skill_power=100, weakness_mult=1.5, crit_mult=1.5)

    attacker_stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    defender_stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats, level=50)
    defender = Combatant(name="Defender", base_stats=defender_stats, level=50)

    scenario = {
        "name": "No buffs",
        "attacker_buffs": {},
        "defender_buffs": {}
    }

    result = run_scenario(engine, attacker, defender, scenario)

    assert result['scenario_name'] == "No buffs"
    assert result['damages']['normal'] == 100.0
    assert result['damages']['normal_weakness'] == 150.0
    assert result['damages']['crit'] == 150.0
    assert result['damages']['crit_weakness'] == 225.0
    assert abs(result['crit_rate'] - 0.05) < 0.001


def test_run_scenario_with_buffs():
    """Test run_scenario applies buffs from scenario config"""
    engine = CombatEngine(skill_power=100, weakness_mult=1.5, crit_mult=1.5)

    attacker_stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    defender_stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats, level=50)
    defender = Combatant(name="Defender", base_stats=defender_stats, level=50)

    scenario = {
        "name": "Buffs test",
        "attacker_buffs": {"STR": 3},
        "defender_buffs": {"VIT": -2}
    }

    result = run_scenario(engine, attacker, defender, scenario)

    # STR: 50 * 1.6 = 80, VIT: 50 * 0.7 = 35
    # Base damage: (80 * 100) / 35 = 228.57...
    assert abs(result['damages']['normal'] - 228.57) < 0.01

    # Buffs should be reset after scenario
    assert attacker.buff_levels['STR'] == 0
    assert defender.buff_levels['VIT'] == 0


def test_run_all_scenarios():
    """Test run_all_scenarios processes all scenarios from config"""
    config = {
        "attacker": {
            "name": "Attacker",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "defender": {
            "name": "Defender",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "scenarios": [
            {"name": "Scenario 1", "attacker_buffs": {}, "defender_buffs": {}},
            {"name": "Scenario 2", "attacker_buffs": {"STR": 2}, "defender_buffs": {}}
        ],
        "formulas": {
            "weakness_multiplier": 1.5,
            "crit_multiplier": 1.5,
            "skill_power": 100
        }
    }

    results = run_all_scenarios(config)

    assert len(results) == 2
    assert results[0]['scenario_name'] == "Scenario 1"
    assert results[1]['scenario_name'] == "Scenario 2"

    # First scenario (baseline) should have percent_change = 0
    assert results[0]['percent_change'] == 0.0

    # Second scenario should show % increase
    assert results[1]['percent_change'] > 0


def test_run_all_scenarios_calculates_percent_change():
    """Test percent_change is calculated relative to baseline"""
    config = {
        "attacker": {
            "name": "Attacker",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "defender": {
            "name": "Defender",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "scenarios": [
            {"name": "Baseline", "attacker_buffs": {}, "defender_buffs": {}},
            {"name": "+3 STR", "attacker_buffs": {"STR": 3}, "defender_buffs": {}}
        ],
        "formulas": {
            "weakness_multiplier": 1.5,
            "crit_multiplier": 1.5,
            "skill_power": 100
        }
    }

    results = run_all_scenarios(config)

    baseline_damage = results[0]['damages']['normal']
    buffed_damage = results[1]['damages']['normal']

    expected_percent_change = ((buffed_damage - baseline_damage) / baseline_damage) * 100

    assert abs(results[1]['percent_change'] - expected_percent_change) < 0.01


def test_print_table_outputs_box_drawing_chars(capsys):
    """Test print_table outputs correctly formatted ASCII table with box chars"""
    config = {
        "attacker": {
            "name": "Attacker",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "defender": {
            "name": "Defender",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "scenarios": [
            {"name": "Baseline", "attacker_buffs": {}, "defender_buffs": {}},
            {"name": "+2 STR", "attacker_buffs": {"STR": 2}, "defender_buffs": {}}
        ],
        "formulas": {
            "weakness_multiplier": 1.5,
            "crit_multiplier": 1.5,
            "skill_power": 100
        }
    }

    results = run_all_scenarios(config)
    print_table(results, "Attacker", "Defender")

    captured = capsys.readouterr()
    output = captured.out

    # Check for box-drawing characters
    assert "┌" in output
    assert "┐" in output
    assert "└" in output
    assert "┘" in output
    assert "├" in output
    assert "┤" in output
    assert "─" in output
    assert "│" in output

    # Check for header elements
    assert "Attacker:" in output
    assert "Defender:" in output
    assert "Baseline damage:" in output
    assert "Crit rate:" in output

    # Check for table columns
    assert "Scenario" in output
    assert "Normal" in output
    assert "% Change" in output
    assert "Weakness" in output
    assert "Expected" in output

    # Check for scenario names
    assert "Baseline" in output
    assert "+2 STR" in output


def test_print_table_empty_results(capsys):
    """Test print_table handles empty results gracefully"""
    print_table([], "Attacker", "Defender")

    captured = capsys.readouterr()
    output = captured.out

    assert "No results to display" in output
