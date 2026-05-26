import json
from typing import Any, Dict, List
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


def run_all_scenarios(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run all scenarios from config and calculate percent changes.

    Args:
        config: Full configuration dictionary

    Returns:
        List of scenario results with percent_change added
    """
    # Initialize engine from config
    engine = CombatEngine(
        weakness_mult=config['formulas']['weakness_multiplier'],
        crit_mult=config['formulas']['crit_multiplier'],
        skill_power=config['formulas']['skill_power']
    )

    # Create combatants
    attacker = Combatant(
        name=config['attacker']['name'],
        base_stats=config['attacker']['stats']
    )
    defender = Combatant(
        name=config['defender']['name'],
        base_stats=config['defender']['stats']
    )

    # Run all scenarios
    results = []
    for scenario in config['scenarios']:
        result = run_scenario(engine, attacker, defender, scenario)
        results.append(result)

    # Calculate percent changes relative to first scenario (baseline)
    if results:
        baseline_damage = results[0]['damages']['normal']

        for result in results:
            current_damage = result['damages']['normal']
            percent_change = ((current_damage - baseline_damage) / baseline_damage) * 100
            result['percent_change'] = percent_change

    return results


def print_table(results: List[Dict[str, Any]], attacker_name: str, defender_name: str) -> None:
    """
    Print formatted ASCII table of scenario results.

    Args:
        results: List of scenario results from run_all_scenarios
        attacker_name: Attacker name for header
        defender_name: Defender name for header
    """
    if not results:
        print("No results to display")
        return

    print("\n" + "=" * 80)
    print("SMTV Combat Simulator")
    print("=" * 80)
    print(f"Attacker: {attacker_name}")
    print(f"Defender: {defender_name}")
    print()

    baseline_damage = results[0]['damages']['normal']
    crit_rate_pct = results[0]['crit_rate'] * 100

    print(f"Baseline damage: {baseline_damage:.1f} (normal hit, no weakness)")
    print(f"Crit rate: {crit_rate_pct:.1f}%")
    print()

    # Table header
    print("┌─" + "─" * 35 + "┬─" + "─" * 10 + "┬─" + "─" * 10 + "┬─" + "─" * 10 + "┬─" + "─" * 10 + "┐")
    print(f"│ {'Scenario':<35}│ {'Normal':<10}│ {'% Change':<10}│ {'Weakness':<10}│ {'Expected':<10}│")
    print("├─" + "─" * 35 + "┼─" + "─" * 10 + "┼─" + "─" * 10 + "┼─" + "─" * 10 + "┼─" + "─" * 10 + "┤")

    # Table rows
    for result in results:
        scenario_name = result['scenario_name'][:35]
        normal_dmg = result['damages']['normal']
        percent_change = result['percent_change']
        weakness_dmg = result['damages']['normal_weakness']
        expected_dmg = result['damages']['expected']

        percent_str = f"+{percent_change:.1f}%" if percent_change >= 0 else f"{percent_change:.1f}%"

        print(f"│ {scenario_name:<35}│ {normal_dmg:>9.1f} │ {percent_str:>9} │ {weakness_dmg:>9.1f} │ {expected_dmg:>9.1f} │")

    # Table footer
    print("└─" + "─" * 35 + "┴─" + "─" * 10 + "┴─" + "─" * 10 + "┴─" + "─" * 10 + "┴─" + "─" * 10 + "┘")
    print()
