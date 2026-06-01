import json
import csv
import os
import sys
import argparse
import statistics
from pathlib import Path
from typing import Any, Dict, List
from copy import deepcopy
from src.combat_engine import CombatEngine, Combatant
from src.visualizer import generate_all_graphs


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
        base_stats=config['attacker']['stats'],
        level=config['attacker'].get('level', 50)
    )
    defender = Combatant(
        name=config['defender']['name'],
        base_stats=config['defender']['stats'],
        level=config['defender'].get('level', 50)
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


def export_csv(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export scenario results to CSV file with detailed damage variants.

    Each scenario produces 6 rows (normal, normal_weakness, crit, crit_weakness,
    expected, expected_weakness damage types).

    Args:
        results: List of scenario results from run_all_scenarios
        output_path: Path to CSV output file

    Raises:
        IOError: If file cannot be written
    """
    # Create output directory if doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define CSV headers
    headers = [
        'scenario_name',
        'attacker_buffs',
        'defender_buffs',
        'hit_type',
        'weakness',
        'crit',
        'damage',
        'crit_rate',
        'percent_change',
        'baseline_damage'
    ]

    # Write CSV
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        # Get baseline damage from first scenario
        baseline_damage = results[0]['damages']['normal'] if results else 0

        # Write one row per damage variant per scenario
        for result in results:
            scenario_name = result['scenario_name']
            attacker_buffs = json.dumps(result['attacker_buffs'])
            defender_buffs = json.dumps(result['defender_buffs'])
            crit_rate = result['crit_rate']
            percent_change = result['percent_change']

            # Damage variants: normal, normal_weakness, crit, crit_weakness, expected, expected_weakness
            variants = [
                ('normal', False, False),
                ('normal_weakness', True, False),
                ('crit', False, True),
                ('crit_weakness', True, True),
                ('expected', False, False),
                ('expected_weakness', True, False)
            ]

            for variant_key, is_weakness, is_crit in variants:
                damage = result['damages'][variant_key]

                writer.writerow({
                    'scenario_name': scenario_name,
                    'attacker_buffs': attacker_buffs,
                    'defender_buffs': defender_buffs,
                    'hit_type': variant_key,
                    'weakness': is_weakness,
                    'crit': is_crit,
                    'damage': f"{damage:.1f}",
                    'crit_rate': f"{crit_rate:.4f}",
                    'percent_change': f"{percent_change:.1f}",
                    'baseline_damage': f"{baseline_damage:.1f}"
                })

    print(f"CSV exported to: {output_path}")


def load_validation_scenario(scenario_path: str) -> Dict[str, Any]:
    """
    Load a validation scenario from JSON file.
    
    Args:
        scenario_path: Path to validation scenario JSON
    
    Returns:
        Validation scenario dictionary
    """
    with open(scenario_path, 'r') as f:
        scenario = json.load(f)
    return scenario


def run_validation_scenario(
    engine: CombatEngine,
    scenario_config: Dict[str, Any],
    num_trials: int = 100
) -> Dict[str, Any]:
    """
    Run a single validation scenario with multiple trials.
    
    Args:
        engine: CombatEngine instance
        scenario_config: Scenario configuration dict
        num_trials: Number of trials to run
    
    Returns:
        Dictionary with mean, std, min, max damage
    """
    attacker_cfg = scenario_config["attacker"]
    defender_cfg = scenario_config["defender"]
    skill_cfg = scenario_config["skill"]
    
    # Create combatants
    attacker = Combatant(
        name=attacker_cfg["name"],
        base_stats=attacker_cfg["stats"],
        level=attacker_cfg["level"],
        skill_potentials=attacker_cfg.get("skill_potentials", {}),
        charge_state=attacker_cfg.get("charge_state"),
        passive_abilities=attacker_cfg.get("passive_abilities", [])
    )
    defender = Combatant(
        name=defender_cfg["name"],
        base_stats=defender_cfg["stats"],
        level=defender_cfg["level"],
        guarding=defender_cfg.get("guarding", False),
        doubler_active=defender_cfg.get("doubler_active", False)
    )
    
    # Apply buffs
    for stat_key, level in attacker_cfg.get("buffs", {}).items():
        if stat_key == "attack" and level != 0:
            attacker.buff_levels['STR'] = level
        elif stat_key == "defense" and level != 0:
            attacker.buff_levels['VIT'] = level
    
    for stat_key, level in defender_cfg.get("buffs", {}).items():
        if stat_key == "attack" and level != 0:
            defender.buff_levels['STR'] = level
        elif stat_key == "defense" and level != 0:
            defender.buff_levels['VIT'] = level
    
    # Run trials
    damages = []
    for _ in range(num_trials):
        damage = engine.calculate_vengeance_damage(
            attacker=attacker,
            defender=defender,
            skill_element=skill_cfg["element"],
            resistance=defender_cfg.get("resistance", "neutral"),
            is_crit=skill_cfg.get("is_crit", False)
        )
        damages.append(damage)
    
    return {
        "name": scenario_config["name"],
        "mean": statistics.mean(damages),
        "std": statistics.stdev(damages) if len(damages) > 1 else 0.0,
        "min": min(damages),
        "max": max(damages),
        "config": scenario_config
    }


def run_validation_suite(
    validation_dir: str,
    num_trials: int = 100
) -> Dict[str, Dict[str, Any]]:
    """
    Run all validation scenarios in directory.
    
    Args:
        validation_dir: Path to directory containing validation JSON files
        num_trials: Number of trials per scenario
    
    Returns:
        Dictionary mapping scenario name to statistics
    """
    engine = CombatEngine(skill_power=100)
    results = {}
    
    validation_path = Path(validation_dir)
    scenario_files = sorted(validation_path.glob("*.json"))
    
    for scenario_file in scenario_files:
        scenario_data = load_validation_scenario(str(scenario_file))
        
        for sub_scenario in scenario_data["scenarios"]:
            result = run_validation_scenario(engine, sub_scenario, num_trials)
            results[result["name"]] = result
    
    return results


def main() -> None:
    """
    Main entry point for SMTV Combat Simulator.

    Parses CLI arguments, loads config, runs all scenarios, prints table,
    exports CSV, generates all graphs, and prints completion summary.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='SMTV Combat Simulator - Calculate damage across multiple scenarios'
    )
    parser.add_argument(
        'config',
        nargs='?',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '--output',
        default='output/results.csv',
        help='Path to CSV output file (default: output/results.csv)'
    )
    parser.add_argument(
        '--output-prefix',
        default='output/',
        help='Path prefix for graph outputs (default: output/)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run validation suite mode'
    )
    parser.add_argument(
        '--validation-dir',
        default='config/validation/',
        help='Path to validation scenarios directory (default: config/validation/)'
    )
    parser.add_argument(
        '--trials',
        type=int,
        default=100,
        help='Number of trials per validation scenario (default: 100)'
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch the Shin Megami Tensei V interactive GUI'
    )
    args = parser.parse_args()

    try:
        # GUI mode
        if args.gui:
            print("Launching SMTV Vengeance Interactive GUI...")
            from src.gui import SMTV_GUI
            app = SMTV_GUI()
            app.mainloop()
            return

        # Validation mode
        if args.validate:
            print(f"Running validation suite from: {args.validation_dir}")
            print(f"Trials per scenario: {args.trials}")
            print()
            
            results = run_validation_suite(args.validation_dir, args.trials)
            
            # Print results table
            print("=" * 80)
            print("VALIDATION RESULTS")
            print("=" * 80)
            print(f"{'Scenario':<50} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10}")
            print("-" * 80)
            
            for scenario_name, stats in results.items():
                print(f"{scenario_name:<50} {stats['mean']:>10.1f} {stats['std']:>10.2f} {stats['min']:>10.1f} {stats['max']:>10.1f}")
            
            print("=" * 80)
            
            # Export CSV
            output_dir = Path("output/validation")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            csv_path = output_dir / "validation_results.csv"
            with open(csv_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['scenario', 'mean', 'std', 'min', 'max'])
                writer.writeheader()
                for scenario_name, stats in results.items():
                    writer.writerow({
                        'scenario': scenario_name,
                        'mean': f"{stats['mean']:.1f}",
                        'std': f"{stats['std']:.2f}",
                        'min': f"{stats['min']:.1f}",
                        'max': f"{stats['max']:.1f}"
                    })
            
            print(f"\nValidation results exported to: {csv_path}")
            
            # Generate validation visualizations
            from src.visualizer import generate_validation_report
            generate_validation_report(results, "output/validation")
            return

        # Load configuration
        config = load_config(args.config)
        print(f"Loaded config from: {args.config}")

        # Run all scenarios
        results = run_all_scenarios(config)

        # Print results table
        print_table(results, config['attacker']['name'], config['defender']['name'])

        # Export CSV
        csv_path = args.output
        export_csv(results, csv_path)

        # Generate all graphs
        engine = CombatEngine(
            weakness_mult=config['formulas']['weakness_multiplier'],
            crit_mult=config['formulas']['crit_multiplier'],
            skill_power=config['formulas']['skill_power']
        )
        attacker = Combatant(
            name=config['attacker']['name'],
            base_stats=config['attacker']['stats'],
            level=config['attacker'].get('level', 50)
        )
        defender = Combatant(
            name=config['defender']['name'],
            base_stats=config['defender']['stats'],
            level=config['defender'].get('level', 50)
        )

        generate_all_graphs(results, engine, attacker, defender, args.output_prefix)

        # Print completion summary
        graph_prefix = args.output_prefix if args.output_prefix.endswith(('/', '_')) else f"{args.output_prefix}_"
        print("\n" + "=" * 80)
        print("SIMULATION COMPLETE")
        print("=" * 80)
        print(f"Results exported to: {args.output}")
        print(f"Graphs generated with prefix: {args.output_prefix}")
        print(f"  - {graph_prefix}scenario_comparison.png")
        print(f"  - {graph_prefix}buff_progression.png")
        print(f"  - {graph_prefix}buff_debuff_matrix.png")
        print("=" * 80)

    except FileNotFoundError as e:
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
