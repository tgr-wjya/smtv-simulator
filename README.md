# SMTV Combat Simulator

A damage calculation simulator for **Shin Megami Tensei V: Vengeance** to analyze buff/debuff mechanics through mathematical modeling.

## Features

- **Physical damage calculation** using SMTV formulas
- **Buff/debuff system** matching SMTV (-3 to +3 levels per stat)
- **Five stats:** STR (attack), VIT (defense), MAG, AGI, LUC (crit rate)
- **Weakness exploitation** with 1.5× damage multiplier
- **Critical hits** based on Luck stat
- **Multiple output formats:**
  - ASCII tables in terminal
  - Matplotlib graphs (bar chart, line chart, heatmap)
  - CSV export for external analysis

## Installation

### Requirements

- Python 3.9+
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
# Run simulator with default config
python3 src/runner.py

# Run with custom config
python3 src/runner.py path/to/custom_config.json
```

### Output

The simulator generates:

1. **ASCII Table** (printed to terminal)
   - Scenario names
   - Normal damage
   - Percent change vs baseline
   - Weakness damage
   - Expected damage (accounting for crit rate)

2. **CSV Export** (`output/results.csv`)
   - One row per damage variant (normal, weakness, crit, etc.)
   - All buff levels
   - Crit rate and percent change

3. **Graphs** (PNG files in `output/`)
   - `scenario_comparison.png` - Bar chart comparing scenarios
   - `buff_progression.png` - Line chart showing damage scaling with buffs
   - `buff_debuff_matrix.png` - Heatmap of buff×debuff combinations

## Configuration

Edit `config.json` to customize:

### Combatant Stats

```json
{
  "attacker": {
    "name": "Nahobino",
    "stats": {
      "STR": 45,
      "VIT": 38,
      "MAG": 42,
      "AGI": 40,
      "LUC": 35
    }
  },
  "defender": {
    "name": "Daemon",
    "stats": {
      "STR": 50,
      "VIT": 55,
      "MAG": 40,
      "AGI": 35,
      "LUC": 30
    }
  }
}
```

### Scenarios

```json
{
  "scenarios": [
    {
      "name": "No buffs (baseline)",
      "attacker_buffs": {},
      "defender_buffs": {}
    },
    {
      "name": "Attacker +3 STR",
      "attacker_buffs": {"STR": 3},
      "defender_buffs": {}
    },
    {
      "name": "Defender -3 VIT",
      "attacker_buffs": {},
      "defender_buffs": {"VIT": -3}
    }
  ]
}
```

**Buff Levels:**
- Range: -3 to +3
- Negative values = debuffs
- Positive values = buffs
- Apply to individual stats or all stats

### Formula Parameters

```json
{
  "formulas": {
    "weakness_multiplier": 1.5,
    "crit_multiplier": 1.5,
    "skill_power": 100
  }
}
```

## How It Works

### Damage Calculation

1. **Effective Stats:** `base_stat × buff_multiplier[buff_level]`
2. **Base Damage:** `(effective_STR × skill_power) / effective_VIT`
3. **Weakness:** `base_damage × weakness_multiplier`
4. **Critical:** `base_damage × crit_multiplier`
5. **Expected Damage:** `normal_dmg × (1 - crit_rate) + crit_dmg × crit_rate`

### Buff Multipliers

| Level | Multiplier |
|-------|------------|
| -3    | 0.6×       |
| -2    | 0.7×       |
| -1    | 0.85×      |
| 0     | 1.0×       |
| +1    | 1.2×       |
| +2    | 1.4×       |
| +3    | 1.6×       |

### Critical Rate

`crit_rate = 5% + (attacker_LUC - defender_LUC) × 0.2%`

Capped at 100%.

## Example Output

```
================================================================================
SMTV Combat Simulator
================================================================================
Attacker: Nahobino
Defender: Daemon

Baseline damage: 81.8 (normal hit, no weakness)
Crit rate: 6.5%

┌───────────────────────────────────┬───────────┬───────────┬───────────┬───────────┐
│ Scenario                          │    Normal │  % Change │  Weakness │  Expected │
├───────────────────────────────────┼───────────┼───────────┼───────────┼───────────┤
│ No buffs (baseline)               │      81.8 │     +0.0% │     122.7 │      84.9 │
│ Attacker +3 STR                   │     130.9 │    +60.0% │     196.4 │     135.9 │
│ Defender -3 VIT                   │     136.4 │    +66.7% │     204.5 │     141.6 │
│ Both maxed (+3 STR, -3 VIT)       │     218.2 │   +166.7% │     327.3 │     226.5 │
└───────────────────────────────────┴───────────┴───────────┴───────────┴───────────┘
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_combat_engine.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Project Structure

```
smtv-simulator/
├── src/
│   ├── combat_engine.py    # Core damage calculation
│   ├── visualizer.py        # Graph generation
│   └── runner.py            # CLI entry point
├── tests/
│   ├── test_combatant.py
│   ├── test_combat_engine.py
│   └── test_runner.py
├── config.json              # Configuration file
├── output/                  # Generated graphs and CSV
├── requirements.txt
└── README.md
```

## License

MIT

## Credits

Design and implementation assisted by Claude Sonnet 4.5
