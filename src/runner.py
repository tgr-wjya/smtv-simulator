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
    Print formatted ASCII table of scenario results with box-drawing characters.

    Args:
        results: List of scenario results from run_all_scenarios
        attacker_name: Name of attacker combatant
        defender_name: Name of defender combatant
    """
    if not results:
        print("No results to display.")
        return

    # Extract baseline info
    baseline_damage = results[0]['damages']['normal']
    baseline_crit_rate = results[0]['crit_rate']

    # Print header
    print()
    print("╔" + "═" * 78 + "╗")
    print(f"║ {attacker_name} vs {defender_name:<57} ║")
    print("╠" + "═" * 78 + "╣")
    print(f"║ Baseline Damage: {baseline_damage:>8.2f}  |  Crit Rate: {baseline_crit_rate:>6.2%}{' ' * 33} ║")
    print("╠" + "═" * 78 + "╣")

    # Table header
    print("║ Scenario" + " " * 20 + "│ Normal   │ % Change │ Weakness │ Expected │")
    print("╠" + "═" * 78 + "╣")

    # Table rows
    for result in results:
        scenario_name = result['scenario_name']
        normal_dmg = result['damages']['normal']
        percent_change = result['percent_change']
        weakness_dmg = result['damages']['normal_weakness']
        expected_dmg = result['damages']['expected']

        # Format scenario name (truncate if needed)
        scenario_col = scenario_name[:27].ljust(27)

        # Build row
        row = f"║ {scenario_col} │ {normal_dmg:>7.1f} │ {percent_change:>7.1f}% │ {weakness_dmg:>7.1f} │ {expected_dmg:>7.1f} │"
        print(row)

    # Footer
    print("╚" + "═" * 78 + "╝")
    print()
