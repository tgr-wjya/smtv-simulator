import pytest
import json
from pathlib import Path
from src.runner import run_validation_suite, load_validation_scenario


def test_load_validation_scenario():
    """Test loading validation scenario from JSON"""
    scenario_path = "config/validation/overleveled_vs_multiplicative.json"
    
    if not Path(scenario_path).exists():
        pytest.skip(f"Validation config not found: {scenario_path}")
    
    scenario = load_validation_scenario(scenario_path)
    
    assert "name" in scenario
    assert "scenarios" in scenario
    assert len(scenario["scenarios"]) >= 2


def test_run_validation_suite():
    """Test validation suite runs without error"""
    validation_dir = "config/validation"
    
    if not Path(validation_dir).exists():
        pytest.skip(f"Validation directory not found: {validation_dir}")
    
    results = run_validation_suite(validation_dir, num_trials=10)
    
    assert len(results) > 0
    
    for scenario_name, stats in results.items():
        assert "mean" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats


def test_multiplicative_dominance():
    """Test that multiplicative stack scenarios produce higher damage than pure level"""
    validation_dir = "config/validation"
    
    if not Path(validation_dir).exists():
        pytest.skip(f"Validation directory not found: {validation_dir}")
    
    results = run_validation_suite(validation_dir, num_trials=20)
    
    # Proof 1: Underleveled + Multipliers > Overleveled
    if "Overleveled (Lv99 vs Lv85)" in results and "Underleveled + Multipliers (Lv80 vs Lv85)" in results:
        assert results["Underleveled + Multipliers (Lv80 vs Lv85)"]["mean"] > results["Overleveled (Lv99 vs Lv85)"]["mean"]
    
    # Proof 2: Tarukaja + Stack > Tarukaja Only
    if "Tarukaja Only" in results and "Tarukaja + Charge + Potential" in results:
        assert results["Tarukaja + Charge + Potential"]["mean"] > results["Tarukaja Only"]["mean"]
