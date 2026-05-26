import json
from typing import Any, Dict
from copy import deepcopy
from src.combat_engine import CombatEngine, Combatant


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.

    Args:
        config_path (str): Path to the JSON configuration file

    Returns:
        dict: Configuration dict with attacker, defender, scenarios, formulas sections

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


def run_scenario(
    engine: CombatEngine,
    attacker: Combatant,
    defender: Combatant,
    scenario: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run a single combat scenario and calculate all damage variants.

    Applies buffs from scenario, calculates damages, then resets buffs.

    Args:
        engine: CombatEngine instance
        attacker: Attacker combatant
        defender: Defender combatant
        scenario: Scenario config with name and buff settings

    Returns:
        Dictionary with scenario name, damages, and crit rate
    """
    # Save original buff levels
    original_attacker_buffs = deepcopy(attacker.buff_levels)
    original_defender_buffs = deepcopy(defender.buff_levels)

    # Apply scenario buffs
    for stat, level in scenario['attacker_buffs'].items():
        attacker.buff_levels[stat] = level

    for stat, level in scenario['defender_buffs'].items():
        defender.buff_levels[stat] = level

    # Calculate all damage variants
    crit_rate = engine.calculate_crit_rate(attacker, defender)

    damages = {
        'normal': engine.calculate_damage(attacker, defender, is_weakness=False, is_crit=False),
        'normal_weakness': engine.calculate_damage(attacker, defender, is_weakness=True, is_crit=False),
        'crit': engine.calculate_damage(attacker, defender, is_weakness=False, is_crit=True),
        'crit_weakness': engine.calculate_damage(attacker, defender, is_weakness=True, is_crit=True),
        'expected': engine.calculate_expected_damage(attacker, defender, is_weakness=False),
        'expected_weakness': engine.calculate_expected_damage(attacker, defender, is_weakness=True)
    }

    # Reset buffs
    attacker.buff_levels = original_attacker_buffs
    defender.buff_levels = original_defender_buffs

    return {
        'scenario_name': scenario['name'],
        'attacker_buffs': scenario['attacker_buffs'],
        'defender_buffs': scenario['defender_buffs'],
        'damages': damages,
        'crit_rate': crit_rate
    }
