# SMTV Combat Simulator Design

**Date:** 2026-05-26  
**Purpose:** Build a combat damage simulator for Shin Megami Tensei V: Vengeance to understand buff/debuff mechanics through mathematical analysis

## Problem Statement

When playing SMTV on Hard difficulty, want to understand the actual mathematical impact of:
- Buffing party stats vs debuffing enemy stats
- Stacking both buffs and debuffs simultaneously
- How weakness exploitation interacts with stat modifications
- Critical hit probability based on Luck stat

Goal is not to look up formulas but to implement and experiment with them to see real damage numbers across different buff/debuff scenarios.

## Requirements

### Core Features
1. **Physical damage calculation** using SMTV formulas
2. **Buff/debuff system** matching SMTV (-3 to +3 levels per stat)
3. **Five stats:** STR (attack), VIT (defense), MAG (unused), AGI (unused), LUC (crit rate)
4. **Weakness system:** 1.5× damage multiplier for hitting physical weakness
5. **Critical hits:** Luck-based crit rate, separate crit damage multiplier
6. **Multiple output views:**
   - Side-by-side scenario comparison (no buffs, buffs only, debuffs only, both)
   - Progressive view (damage at each buff level: 0, +1, +2, +3)
   - Matrix view (buff level × debuff level grid)
7. **Percentage change tracking** relative to baseline (no buffs)
8. **Both individual and all-stat buffs:** Apply +2 STR only, or +1 to all stats

### Output Requirements
- ASCII tables in terminal with absolute damage and % change
- Matplotlib graphs (heatmaps, line charts, bar charts)
- CSV export for LLM analysis (columns: scenario, buff levels, damage, % change, crit rate)
- All graphs saved as PNG files

### Extensibility
- Stat values configurable via JSON
- Formula parameters tunable (weakness multiplier, crit multiplier)
- Should be able to extrapolate beyond +3 buffs if formula is linear

## Architecture

### Component Overview

```
smtv-simulator/
├── combat_engine.py      # Core damage calculation logic
├── runner.py             # CLI entry point, scenario execution
├── visualizer.py         # Graph generation (matplotlib)
├── config.json           # Stat definitions and test scenarios
├── output/               # Generated graphs and CSV exports
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-05-26-smtv-combat-simulator-design.md
```

### Dependencies
- Python 3.9+
- matplotlib (graphs)
- numpy (statistical calculations)
- Standard library: json, csv, dataclasses

## Component Details

### 1. combat_engine.py

**Classes:**

#### `Combatant`
Stores entity stats and buff state.

```python
@dataclass
class Combatant:
    name: str
    base_stats: dict[str, int]  # {'STR': 45, 'VIT': 38, ...}
    buff_levels: dict[str, int] # {'STR': 0, 'VIT': -1, ...} (-3 to +3)
    
    def get_effective_stat(self, stat: str) -> float:
        """Returns base_stat * buff_multiplier"""
    
    def apply_buff(self, stat: str, delta: int):
        """Change buff level, clamped to [-3, +3]"""
    
    def apply_all_buffs(self, delta: int):
        """Apply same delta to all stats"""
```

#### `CombatEngine`
Damage calculation and formula logic.

```python
class CombatEngine:
    BUFF_MULTIPLIERS = {
        -3: 0.6,
        -2: 0.7,
        -1: 0.85,
        0: 1.0,
        +1: 1.2,
        +2: 1.4,
        +3: 1.6
    }
    
    def __init__(self, weakness_mult=1.5, crit_mult=1.5, skill_power=100):
        self.weakness_multiplier = weakness_mult
        self.crit_multiplier = crit_mult
        self.skill_power = skill_power
    
    def calculate_base_damage(self, attacker: Combatant, defender: Combatant) -> float:
        """
        Formula: (attacker_effective_STR * skill_power) / defender_effective_VIT
        Plus variance/randomness (±5-10%)
        """
    
    def calculate_crit_rate(self, attacker: Combatant, defender: Combatant) -> float:
        """
        Crit rate based on LUC difference
        Formula: TBD from research
        """
    
    def calculate_damage(
        self, 
        attacker: Combatant, 
        defender: Combatant,
        is_weakness: bool = False,
        is_crit: bool = False
    ) -> float:
        """
        Full damage calculation:
        1. Base damage with buffs applied
        2. Apply weakness multiplier if applicable
        3. Apply crit multiplier if applicable
        """
    
    def calculate_expected_damage(
        self,
        attacker: Combatant,
        defender: Combatant,
        is_weakness: bool = False
    ) -> float:
        """
        Expected value: normal_dmg * (1 - crit_rate) + crit_dmg * crit_rate
        """
```

**Research Notes:**
- SMTV buff multiplier values need verification (will research datamined formulas)
- Crit rate formula depends on attacker.LUC and defender.LUC (typical: higher LUC = more crits)
- Crit damage multiplier may be 1.5× or 2× (research needed)
- Base damage may include level scaling or additional factors (simplify if not documented)

### 2. runner.py

CLI script that orchestrates simulation.

```python
def load_config(config_path: str) -> dict:
    """Load JSON config with stats and scenarios"""

def run_scenario(
    engine: CombatEngine,
    attacker: Combatant,
    defender: Combatant,
    scenario: dict
) -> dict:
    """
    Apply buffs from scenario config, calculate:
    - Normal damage (no weakness, no crit)
    - Normal damage with weakness
    - Crit damage (no weakness)
    - Crit damage with weakness
    - Expected damage (weighted by crit rate)
    
    Returns: {
        'scenario_name': str,
        'attacker_buffs': dict,
        'defender_buffs': dict,
        'damages': {
            'normal': float,
            'normal_weakness': float,
            'crit': float,
            'crit_weakness': float,
            'expected': float,
            'expected_weakness': float
        },
        'crit_rate': float,
        'percent_change': float  # vs baseline
    }
    """

def run_all_scenarios(config: dict) -> list[dict]:
    """Run all scenarios from config, return results"""

def print_table(results: list[dict]):
    """Pretty-print ASCII table with damage and % change"""

def export_csv(results: list[dict], output_path: str):
    """Export detailed results to CSV"""

def main():
    config = load_config('config.json')
    engine = CombatEngine(
        weakness_mult=config['formulas']['weakness_multiplier'],
        crit_mult=config['formulas']['crit_multiplier'],
        skill_power=config['formulas']['skill_power']
    )
    
    results = run_all_scenarios(config)
    
    # Terminal output
    print_table(results)
    
    # Export CSV
    export_csv(results, 'output/results.csv')
    
    # Generate graphs
    from visualizer import generate_all_graphs
    generate_all_graphs(results, output_dir='output/')
```

### 3. visualizer.py

Matplotlib graph generation.

```python
def generate_scenario_comparison(results: list[dict], output_path: str):
    """
    Bar chart comparing scenarios
    X-axis: scenario names
    Y-axis: damage (bars grouped by: normal, weakness, crit, crit+weakness)
    % change labels on top of bars
    """

def generate_progressive_buff_chart(results: list[dict], output_path: str):
    """
    Line chart showing damage progression
    X-axis: buff level (0, +1, +2, +3)
    Y-axis: damage
    Multiple lines for different debuff levels on defender
    """

def generate_buff_debuff_matrix(
    engine: CombatEngine,
    attacker: Combatant,
    defender: Combatant,
    output_path: str
):
    """
    Heatmap: attacker buff level (x) vs defender debuff level (y)
    Cell color = expected damage
    Annotations show exact damage values
    """

def generate_all_graphs(results: list[dict], output_dir: str):
    """Generate all graph types, save to output_dir"""
```

### 4. config.json

User-editable test configuration.

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
  },
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
      "name": "Attacker +1 all stats",
      "attacker_buffs": {"STR": 1, "VIT": 1, "MAG": 1, "AGI": 1, "LUC": 1},
      "defender_buffs": {}
    },
    {
      "name": "Defender -3 VIT",
      "attacker_buffs": {},
      "defender_buffs": {"VIT": -3}
    },
    {
      "name": "Defender -1 all stats",
      "attacker_buffs": {},
      "defender_buffs": {"STR": -1, "VIT": -1, "MAG": -1, "AGI": -1, "LUC": -1}
    },
    {
      "name": "Both maxed (+3 STR, -3 VIT)",
      "attacker_buffs": {"STR": 3},
      "defender_buffs": {"VIT": -3}
    },
    {
      "name": "Full buff/debuff stack",
      "attacker_buffs": {"STR": 3, "VIT": 3, "MAG": 3, "AGI": 3, "LUC": 3},
      "defender_buffs": {"STR": -3, "VIT": -3, "MAG": -3, "AGI": -3, "LUC": -3}
    }
  ],
  "formulas": {
    "weakness_multiplier": 1.5,
    "crit_multiplier": 1.5,
    "skill_power": 100
  }
}
```

## Damage Calculation Flow

### Step-by-step

1. **Load combatants** from config with base stats
2. **Apply buffs** per scenario (modify buff_levels dict)
3. **Calculate effective stats:**
   ```
   effective_STR = base_STR * BUFF_MULTIPLIERS[buff_level]
   effective_VIT = base_VIT * BUFF_MULTIPLIERS[buff_level]
   ```
4. **Base damage:**
   ```
   base_damage = (effective_STR * skill_power) / effective_VIT
   ```
   Add random variance (±5-10%) if desired for realism
5. **Weakness damage:**
   ```
   weakness_damage = base_damage * weakness_multiplier
   ```
6. **Critical damage:**
   ```
   crit_damage = base_damage * crit_multiplier
   crit_weakness_damage = base_damage * weakness_multiplier * crit_multiplier
   ```
7. **Expected damage:**
   ```
   crit_rate = calculate_crit_rate(attacker.LUC, defender.LUC)
   expected = base_damage * (1 - crit_rate) + crit_damage * crit_rate
   expected_weakness = weakness_damage * (1 - crit_rate) + crit_weakness_damage * crit_rate
   ```
8. **Calculate % change:**
   ```
   percent_change = ((current_damage - baseline_damage) / baseline_damage) * 100
   ```

## Output Format

### ASCII Table Example

```
SMTV Combat Simulator
Attacker: Nahobino (STR:45, VIT:38, MAG:42, AGI:40, LUC:35)
Defender: Daemon (STR:50, VIT:55, MAG:40, AGI:35, LUC:30)

Baseline (No buffs): 150 damage (normal, no weakness)

┌────────────────────────────┬─────────┬─────────┬──────────┬──────────────┐
│ Scenario                   │ Normal  │ % Gain  │ Weakness │ Expected     │
├────────────────────────────┼─────────┼─────────┼──────────┼──────────────┤
│ No buffs (baseline)        │ 150     │ 0%      │ 225      │ 165 (10% CR) │
│ Attacker +3 STR            │ 240     │ +60%    │ 360      │ 264          │
│ Defender -3 VIT            │ 270     │ +80%    │ 405      │ 297          │
│ Both (+3 STR, -3 VIT)      │ 384     │ +156%   │ 576      │ 422          │
│ Full stack                 │ 512     │ +241%   │ 768      │ 563          │
└────────────────────────────┴─────────┴─────────┴──────────┴──────────────┘

Critical Hit Info:
- Crit Rate: 10% (based on LUC difference)
- Crit Multiplier: 1.5×
- Expected damage accounts for crit probability
```

### CSV Export Columns

```
scenario_name, attacker_STR_buff, attacker_VIT_buff, attacker_MAG_buff, attacker_AGI_buff, attacker_LUC_buff, defender_STR_buff, defender_VIT_buff, defender_MAG_buff, defender_AGI_buff, defender_LUC_buff, hit_type, weakness, crit, damage, crit_rate, percent_change, baseline_damage
```

Each row is one damage calculation (normal, weakness, crit, crit+weakness) for one scenario.

### Graph Types

1. **Scenario Bar Chart** (`scenario_comparison.png`)
   - X-axis: scenario names
   - Y-axis: damage
   - Grouped bars: normal, weakness, crit, crit+weakness
   - % change labels above bars

2. **Progressive Line Chart** (`buff_progression.png`)
   - X-axis: attacker buff level (0, +1, +2, +3)
   - Y-axis: damage
   - Multiple lines: defender at -3, -2, -1, 0 VIT debuff
   - Shows damage scaling as buffs increase

3. **Heatmap Matrix** (`buff_debuff_matrix.png`)
   - X-axis: attacker STR buff level (-3 to +3)
   - Y-axis: defender VIT debuff level (-3 to +3)
   - Color intensity: damage amount
   - Annotations: exact damage values in cells

## Implementation Plan

Detailed implementation will be handled by writing-plans skill.

High-level steps:
1. Research SMTV damage formulas (buff multipliers, crit rate formula)
2. Implement `Combatant` and `CombatEngine` classes
3. Write scenario runner and table output
4. Implement CSV export
5. Build visualizer with matplotlib graphs
6. Create default config.json
7. Test with user-provided stat examples
8. Document usage in README

## Open Questions / Research Needed

1. **Exact buff multiplier values** — need to verify -3 to +3 multipliers (assumed 0.6 to 1.6)
2. **Crit rate formula** — how does LUC difference map to crit %? Linear or curved?
3. **Crit damage multiplier** — is it 1.5× or 2×?
4. **Base damage variance** — does SMTV use random ±X% variance? If so, how much?
5. **Level scaling** — does attacker/defender level affect damage? (Assume not for simplicity unless user specifies)
6. **Skill power normalization** — using 100 as default, but does SMTV use different values for standard physical attacks?

Will research these during implementation. If documentation unavailable, will use reasonable assumptions and make them configurable.

## Success Criteria

Simulator is complete when:
- ✓ Can input attacker/defender stats via JSON
- ✓ Can specify individual stat buffs or all-stat buffs
- ✓ Outputs ASCII table with damage and % change
- ✓ Generates 3 graph types (bar, line, heatmap)
- ✓ Exports CSV for LLM analysis
- ✓ Shows normal, weakness, crit, and expected damage
- ✓ User can see clear difference between:
  - Buffs only
  - Debuffs only
  - Both combined
- ✓ Formula can extrapolate beyond +3 if linear

User will provide real stat examples from their SMTV playthrough for validation.
