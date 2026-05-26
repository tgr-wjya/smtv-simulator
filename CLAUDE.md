# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SMTV Combat Simulator - damage calculation simulator for Shin Megami Tensei V: Vengeance. Analyzes buff/debuff mechanics through mathematical modeling. Outputs ASCII tables, matplotlib graphs, and CSV exports.

## Core Architecture

**Three-module design:**

1. **`src/combat_engine.py`** - Core damage calculation logic
   - `Combatant` dataclass: stores entity stats (STR/VIT/MAG/AGI/LUC) and buff state (-3 to +3 per stat)
   - `CombatEngine` class: implements SMTV damage formulas
   - `BUFF_MULTIPLIERS` constant: maps buff levels to multipliers (0.6× at -3 to 1.6× at +3)

2. **`src/runner.py`** - Scenario orchestration and I/O
   - `load_config()`: reads JSON config with attacker/defender stats and scenarios
   - `run_scenario()`: applies buffs, calculates 6 damage variants (normal, weakness, crit, expected), resets buffs
   - `run_all_scenarios()`: executes all scenarios, calculates percent change vs baseline
   - `print_table()`: ASCII table output with box-drawing characters
   - `export_csv()`: detailed CSV export (one row per damage variant)
   - `main()`: CLI entry point

3. **`src/visualizer.py`** - Matplotlib graph generation
   - `generate_scenario_comparison()`: grouped bar chart (4 bars per scenario)
   - `generate_progressive_buff_chart()`: line chart showing damage scaling (-3 to +3)
   - `generate_buff_debuff_matrix()`: heatmap of all buff×debuff combinations
   - `generate_all_graphs()`: wrapper calling all three

**Key design pattern:** Buffs are temporarily applied during scenario execution then reset. Use `deepcopy` to preserve original state. Damage calculation order: base → weakness mult → crit mult.

## Commands

```bash
# Run simulator with default config
python3 -m src.runner

# Run with custom config
python3 -m src.runner path/to/config.json

# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_combat_engine.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Install dependencies
pip install -r requirements.txt
```

## SMTV Damage Formulas

**Base damage:** `(effective_STR × skill_power) / effective_VIT`

**Effective stat:** `base_stat × BUFF_MULTIPLIERS[buff_level]`

**Crit rate:** `5% + (attacker_LUC - defender_LUC) × 0.2%`, capped [0%, 100%]

**Expected damage:** `normal_dmg × (1 - crit_rate) + crit_dmg × crit_rate`

## Configuration Structure

`config.json` defines:
- **attacker/defender stats**: 5 stats (STR, VIT, MAG, AGI, LUC)
- **scenarios**: list of buff/debuff configurations to test
- **formulas**: weakness_multiplier (1.5), crit_multiplier (1.5), skill_power (100)

Buff levels range [-3, +3]. Empty dict `{}` = no buffs. Can specify individual stats or apply to all.

## Testing Strategy

TDD-developed codebase. 24 unit tests covering:
- Combatant buff application and stat calculation
- CombatEngine damage formulas (base, crit rate, full damage, expected damage)
- Runner config loading and scenario execution

Tests use exact assertions for deterministic calculations, tolerance `< 0.01` for floating-point results.

## Output Files

All outputs generated in `output/`:
- `results.csv`: 6 rows per scenario (normal, normal_weakness, crit, crit_weakness, expected, expected_weakness)
- `scenario_comparison.png`: grouped bar chart with percent change labels
- `buff_progression.png`: line chart (4 lines for defender debuff levels 0, -1, -2, -3)
- `buff_debuff_matrix.png`: 7×7 heatmap with text annotations

## Module Imports

Use absolute imports with `src.` prefix:
```python
from src.combat_engine import CombatEngine, Combatant
from src.visualizer import generate_all_graphs
```

This allows running as Python module: `python3 -m src.runner`
