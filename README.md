# SMTV Combat Simulator

A damage calculation simulator for **Shin Megami Tensei V: Vengeance** to analyze buff/debuff mechanics through mathematical modeling.

## Table of Contents

- [Key Insights: Why Debuffs Beat Buffs](#key-insights-why-debuffs-beat-buffs)
  - [The Math Behind It](#the-math-behind-it)
  - [Skill Comparisons](#skill-comparisons)
    - [Single-Target Buffs: Tarukaja vs Rakunda](#single-target-buffs-tarukaja-vs-rakunda)
    - [Team Buff Skills: Turn Efficiency](#team-buff-skills-turn-efficiency)
    - [Stacking Strategy: When to Use Both](#stacking-strategy-when-to-use-both)
    - [LUC and Critical Hits](#luc-and-critical-hits)
  - [Strategic Recommendations](#strategic-recommendations)
- [Features](#features)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Setup](#setup)
- [Usage](#usage)
  - [Quick Start](#quick-start)
  - [Output](#output)
- [Configuration](#configuration)
  - [Combatant Stats](#combatant-stats)
  - [Scenarios](#scenarios)
  - [Formula Parameters](#formula-parameters)
- [How It Works](#how-it-works)
  - [Damage Calculation Flow](#damage-calculation-flow)
  - [Buff Multipliers](#buff-multipliers)
  - [Critical Rate Formula](#critical-rate-formula)
  - [Formula Sources](#formula-sources)
  - [Understanding Expected Damage](#understanding-expected-damage)
- [Practical Examples](#practical-examples)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [Advanced Usage](#advanced-usage)
- [Project Structure](#project-structure)
- [FAQ](#faq)
- [Performance Notes](#performance-notes)
- [Future Enhancements](#future-enhancements)
- [License](#license)
- [Credits](#credits)
- [Support](#support)

## Key Insights: Multiplicative Stacking & Bounded Scaling

Systematic reverse-engineering of the SMTV: Vengeance combat engine reveals that the classic "Level Scaling vs. Stat Scaling" debate is a **false dichotomy**. Bounded mechanics and diminishing returns ensure that **multiplicative optimization** of tactical multipliers reigns supreme.

### 1. Bounded Level Correction (No Infinite Scaling)
In the original SMTV game, level deficits suppression dominated combat entirely. In Vengeance, this is strictly capped:
- **Level deficit penalty** has a hardcoded floor of **0.5x**.
- **Level advantage bonus** has a strict ceiling of **1.5x**.
- **Near-peer encounters** (within ±2 levels) bypass level correction entirely (1.0x).
This 0.5x–1.5x bounds constraint means level deficit is no longer an insurmountable barrier, merely a manageable 50% modifier.

### 2. Stat Diminishing Returns (The Root Cap)
Raw stat-dumping is heavily penalized by the **dynamic Root threshold**:
```
Root = Level + 10
```
- **Linear Phase** (*stat ≤ Root*): Conversion rate is highly efficient (`Offense = Stat × 2`).
- **Penalty Phase** (*stat > Root*): Extra stats suffer a square root mitigation penalty (`Offense = Root + √(Stat - Root) + Root`).
*Example at Level 99 (Root = 109)*: Allocating an additional 141 stats (109 → 250 MAG) only increases actual Offense by **47 points**. Efficient builds allocate stats to reach the Root cap and focus remaining resources elsewhere.

### 3. The Tri-Tiered Vitality Engine
The interaction of Offense vs. Vitality is non-linear and divided into three mathematical tiers:
- **Tier 1 (Heavy Mitigation)**: Triggered when `(Offense - VIT) ≤ Offense/2`. Heavily Suppresses damage using square root dampeners.
- **Tier 2 (Standard Penetration)**: Linear stat penetration (`Base Damage = Offense - VIT`).
- **Tier 3 (Overwhelming Force)**: Triggered when `(Offense - VIT) > 3/4 * Offense`. Reduces scaling growth to curb infinite damage numbers.

### 4. Multiplicative Stacking Synergy (The Real Meta)
Because Level and Stats are bounded, late-game throughput is entirely driven by compounding independent multipliers:
- **Skill Potential**: Up to **1.55x** bonus (at +9 Potential).
- **Charge States**: **1.8x** (Charge/Concentrate) up to **3.4x** (*Impaler's Glory*).
- **Passive Abilities**: *Critical Zealot* adds a separate **1.45x** multiplier to critical hits.
- **Elemental Weakness**: Additive **1.75x** when combined with critical hits.
Optimizing this multiplication chain (e.g., Potential +9 × Impaler's Glory × Critical Zealot = **7.64x** damage) easily dwarfs any theoretical level or stat advantage in isolation.

### Strategic Recommendations
1. **Optimize Multipliers First**: Prioritize elemental Potentials, Charge states, and passive synergies.
2. **Respect the Root Cap**: Stop dumping raw stats once you clear the `Level + 10` threshold; allocate resources to secondary party members.
3. **Buffs and Debuffs are Secondary**: Buffs (Tarukaja) and debuffs (Rakunda) are important, but act as simple multipliers (+20% / +15%) in a much larger chain. Use them to stack, but do not rely on them as primary damage drivers.


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
- virtualenv (recommended)

### Setup

```bash
# Clone or navigate to project directory
cd smtv-simulator

# Create virtual environment (recommended)
python3 -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** You'll see `(.venv)` prefix in terminal when virtual environment active. Deactivate with `deactivate` command.

## Usage

### Quick Start

```bash
# Run simulator with default config
python3 -m src.runner

# Run with custom config
python3 -m src.runner path/to/custom_config.json

# Run with custom output files (for batch analysis)
python3 -m src.runner configs/batch_1_progressive.json \
  --output output/batch_1_progressive_buffs.csv \
  --output-prefix output/batch_1_
```

### Validation Mode

Validate SMTV Vengeance mechanics claims by running the complete mechanics validation suite:

```bash
# Run validation suite (runs 6 validation scenarios proving multiplicative dominance)
python3 -m src.runner --validate

# Run validation suite with custom number of trials (default: 100)
python3 -m src.runner --validate --trials 1000
```

Results are exported to `output/validation/`:
- `validation_results.csv` - Statistics for each scenario
- `multiplier_breakdown.png` - Stacked bar chart showing damage contribution by layer
- `level_vs_multiplicative.png` - Grouped bar chart comparing level advantage vs multiplier stack
- `root_curve.png` - Root diminishing returns curve showing stat dumping cap
- `vitality_heatmap.png` - Heatmap showing the 3-tier Vitality damage boundaries
- `variance_distribution.png` - Stochastic variance distribution histogram

### Interactive GUI Mode

Launch the Shin Megami Tensei V: Vengeance interactive desktop dashboard to design your own Nahobino and calculate damage live:

```bash
python3 -m src.runner --gui
```

**Features:**
- **Nahobino Designer (Left Panel)**: Dynamically adjust level, stats (STR, MAG, LUC), potential modifiers, charge states (None, Charge, Concentrate, Impaler's Glory), and passives (Critical Zealot, Murderous Glee).
- **Target & Buff Designer (Middle Panel)**: Change defender stats, level, elemental resistance, guarding/doubler-bug toggles, and buff levels (-3 to +3).
- **Damage Dashboard & Live Plotting (Right Panel)**: View live damage outputs (Normal, Crit, Expected) and trace how STR buffs scale dynamically via the live matplotlib line graph.

### Output

The simulator generates three types of output:

#### 1. Terminal Output (ASCII Table)

Printed immediately when simulation runs:

```
================================================================================
SMTV Combat Simulator
================================================================================
Attacker: Nahobino
Defender: Daemon

Baseline damage: 81.8 (normal hit, no weakness)
Crit rate: 6.0%

┌────────────────────────────────────┬───────────┬───────────┬───────────┬───────────┐
│ Scenario                           │ Normal    │ % Change  │ Weakness  │ Expected  │
├────────────────────────────────────┼───────────┼───────────┼───────────┼───────────┤
│ No buffs (baseline)                │      81.8 │     +0.0% │     122.7 │      84.3 │
│ Attacker +3 STR                    │     130.9 │    +60.0% │     196.4 │     134.8 │
│ Defender -3 VIT                    │     136.4 │    +66.7% │     204.5 │     140.5 │
│ Both maxed (+3 STR, -3 VIT)        │     218.2 │   +166.7% │     327.3 │     224.7 │
└────────────────────────────────────┴───────────┴───────────┴───────────┴───────────┘
```

**Column meanings:**
- **Normal:** Standard hit damage (no weakness, no crit)
- **% Change:** Percent increase vs baseline (first scenario in your config)
- **Weakness:** Damage when hitting elemental weakness (×1.5 multiplier)
- **Expected:** Weighted average accounting for crit rate probability

**Reading the output:**
- Compare % Change to see relative buff effectiveness
- Expected damage = most realistic damage per hit over many attacks
- Baseline row (first scenario) always shows 0% change

#### 2. CSV Export (`output/results.csv`)

Detailed data export with one row per damage variant:

```csv
scenario_name,attacker_buffs,defender_buffs,hit_type,weakness,crit,damage,crit_rate,percent_change,baseline_damage
No buffs (baseline),{},{},normal,False,False,81.8,0.0600,0.0,81.8
No buffs (baseline),{},{},normal_weakness,True,False,122.7,0.0600,0.0,81.8
No buffs (baseline),{},{},crit,False,True,122.7,0.0600,0.0,81.8
Attacker +3 STR,"{""STR"": 3}",{},normal,False,False,130.9,0.0600,60.0,81.8
```

**Six rows per scenario:**
1. `normal` - Standard hit, no weakness
2. `normal_weakness` - Weakness hit, no crit
3. `crit` - Critical hit, no weakness
4. `crit_weakness` - Critical + weakness combined
5. `expected` - Probability-weighted normal damage
6. `expected_weakness` - Probability-weighted weakness damage

**Use cases:**
- Import into Excel/Google Sheets for custom analysis
- Generate your own graphs
- Compare multiple simulation runs
- Statistical analysis of buff effectiveness

#### 3. Graphs (PNG files in `output/`)

Three visualization types generated automatically:

**`scenario_comparison.png`** - Grouped bar chart
- Four bars per scenario: normal, weakness, crit, expected
- Percent change labels on bars
- Use to visually compare scenario effectiveness

**`buff_progression.png`** - Line chart
- Shows damage scaling from -3 to +3 buff levels
- Four lines representing defender debuff levels (0, -1, -2, -3)
- Demonstrates how buffs stack with debuffs
- X-axis: attacker STR buff level
- Y-axis: damage output

**`buff_debuff_matrix.png`** - Heatmap
- 7×7 grid of all buff×debuff combinations
- Color intensity = damage (darker = higher)
- Numbers in cells show exact damage values
- X-axis: attacker STR buffs (-3 to +3)
- Y-axis: defender VIT debuffs (-3 to +3)
- Use to find optimal buff/debuff combinations

**Opening graphs:**
- Files saved as PNG images in `output/` directory
- Open with any image viewer
- High resolution suitable for presentations/analysis

## Configuration

Edit `config.json` to customize your simulation. Config has three sections:

### Combatant Stats

Define attacker and defender base stats (before buffs):

```json
{
  "attacker": {
    "name": "Nahobino",
    "stats": {
      "STR": 45,  // Attack power (higher = more damage)
      "VIT": 38,  // Defense (not used in damage dealt, only for taking hits)
      "MAG": 42,  // Magic power (not used in physical damage)
      "AGI": 40,  // Speed (not used currently)
      "LUC": 35   // Luck (affects crit rate)
    }
  },
  "defender": {
    "name": "Daemon",
    "stats": {
      "STR": 50,  // Not used in defense
      "VIT": 55,  // Defense (higher = less damage taken)
      "MAG": 40,  // Not used currently
      "AGI": 35,  // Not used currently
      "LUC": 30   // Affects crit rate (defender LUC lowers attacker crit rate)
    }
  }
}
```

**For physical damage simulation:**
- **Attacker STR** and **Defender VIT** are most important
- **LUC difference** affects crit rate: `5% base + (attacker_LUC - defender_LUC) × 0.2%`
- Other stats included for future expansion (magic damage, turn order)

**Stat ranges:**
- Typical SMTV stats: 10-99
- Endgame builds: 40-80 range
- Use actual in-game stats for realistic results

### Scenarios

List of buff/debuff situations to test. **First scenario = baseline** (used for % change calculations):

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
    },
    {
      "name": "Both maxed (+3 STR, -3 VIT)",
      "attacker_buffs": {"STR": 3},
      "defender_buffs": {"VIT": -3}
    }
  ]
}
```

**Buff notation:**
- `{}` = no buffs/debuffs
- `{"STR": 3}` = +3 STR buff (single stat)
- `{"STR": -2}` = -2 STR debuff (negative values)
- `{"STR": 1, "VIT": 1}` = +1 to multiple stats

**Buff level range:** -3 to +3
- **-3:** Rakukaja ×3 (60% of base stat)
- **-2:** Rakukaja ×2 (70%)
- **-1:** Rakukaja ×1 (85%)
- **0:** No buff (100%)
- **+1:** Tarukaja ×1 (120%)
- **+2:** Tarukaja ×2 (140%)
- **+3:** Tarukaja ×3 (160%)

**Common scenario patterns:**

```json
// Test single buff stacking
{"name": "STR +1", "attacker_buffs": {"STR": 1}, "defender_buffs": {}},
{"name": "STR +2", "attacker_buffs": {"STR": 2}, "defender_buffs": {}},
{"name": "STR +3", "attacker_buffs": {"STR": 3}, "defender_buffs": {}},

// Test buff vs debuff effectiveness
{"name": "ATK buff +3", "attacker_buffs": {"STR": 3}, "defender_buffs": {}},
{"name": "DEF debuff -3", "attacker_buffs": {}, "defender_buffs": {"VIT": -3}},

// Test buff stacking caps
{"name": "Overkill", "attacker_buffs": {"STR": 3, "LUC": 3}, "defender_buffs": {"VIT": -3, "LUC": -3}},

// Test all-stat buffs (Luster Candy / Debilitate)
{"name": "Luster Candy", "attacker_buffs": {"STR": 2, "VIT": 2, "MAG": 2, "AGI": 2, "LUC": 2}, "defender_buffs": {}},
{"name": "Debilitate", "attacker_buffs": {}, "defender_buffs": {"STR": -2, "VIT": -2, "MAG": -2, "AGI": -2, "LUC": -2}}
```

**Important:** Always include baseline scenario (no buffs) as first entry for accurate % change calculations.

### Formula Parameters

Adjust game mechanics constants:

```json
{
  "formulas": {
    "weakness_multiplier": 1.5,  // Damage multiplier when hitting weakness
    "crit_multiplier": 1.5,       // Damage multiplier on critical hit
    "skill_power": 100            // Base skill power (typical physical skill)
  }
}
```

**Common skill_power values:**
- Light physical skills: 80-120
- Medium physical skills: 140-180
- Heavy physical skills: 200-250
- Severe physical skills: 300+

**When to change multipliers:**
- Default 1.5× matches SMTV base game
- Some mods or game modes use different values
- Test "what if" scenarios (e.g., 2.0× weakness in hard mode)

## How It Works

### Damage Calculation Flow

The simulator calculates damage in this order:

1. **Apply buffs to base stats:**
   ```
   effective_STR = attacker_base_STR × BUFF_MULTIPLIERS[buff_level]
   effective_VIT = defender_base_VIT × BUFF_MULTIPLIERS[buff_level]
   ```

2. **Calculate base damage:**
   ```
   base_damage = (effective_STR × skill_power) / effective_VIT
   ```

3. **Apply multipliers for variants:**
   - **Normal hit:** `base_damage` (no multipliers)
   - **Weakness hit:** `base_damage × weakness_multiplier` (usually 1.5×)
   - **Critical hit:** `base_damage × crit_multiplier` (usually 1.5×)
   - **Crit + weakness:** `base_damage × weakness_multiplier × crit_multiplier` (2.25×)

4. **Calculate expected damage (probability-weighted):**
   ```
   crit_rate = 5% + (attacker_LUC - defender_LUC) × 0.2%
   expected_damage = normal_damage × (1 - crit_rate) + crit_damage × crit_rate
   ```

### Buff Multipliers

These match SMTV Vengeance mechanics:

| Buff Level | Multiplier | In-Game Equivalent |
|------------|------------|-------------------|
| -3         | 0.6×       | Rakunda ×3        |
| -2         | 0.7×       | Rakunda ×2        |
| -1         | 0.85×      | Rakunda ×1        |
| 0          | 1.0×       | No buffs          |
| +1         | 1.2×       | Tarukaja ×1       |
| +2         | 1.4×       | Tarukaja ×2       |
| +3         | 1.6×       | Tarukaja ×3       |

**Example:**
- Base STR = 45
- +3 STR buff applied
- Effective STR = 45 × 1.6 = 72

**Stacking:**
- Buffs don't multiply with each other (no 1.2 × 1.2)
- Each stat has independent buff level
- Buff level capped at -3 and +3 (casting Tarukaja at +3 does nothing)

### Critical Rate Formula

```
crit_rate = 5% + (attacker_LUC - defender_LUC) × 0.2%
```

Capped at 0% minimum, 100% maximum.

**Examples:**
- Attacker LUC 35, Defender LUC 30: `5% + (5 × 0.2%) = 6%`
- Attacker LUC 50, Defender LUC 20: `5% + (30 × 0.2%) = 11%`
- Attacker LUC 99, Defender LUC 10: `5% + (89 × 0.2%) = 22.8%`

**Effect of LUC buffs:**
- Each +1 attacker LUC buff = +20% more LUC stat
- +3 LUC buff on base 35 = 56 effective LUC
- Debuffing defender LUC increases your crit rate

### Formula Sources

Damage formula and multipliers in simulator follow community-researched SMTV mechanics:

**Damage Formula (STR / VIT relationship):**
- Source: [Megami Tensei Wiki - SMT V Battle Mechanics](https://megamitensei.fandom.com/wiki/Shin_Megami_Tensei_V/Battle_Mechanics)
- Cross-checked against simulator batch outputs in this repository

**Buff Multiplier Values (-3 to +3):**
- Source: [SMT V GameFAQs Guide by Penguin_Knight](https://gamefaqs.gamespot.com/switch/315041-shin-megami-tensei-v/faqs/79611)
- Matches multiplier table used in `src/combat_engine.py`

**Critical Rate Formula (5% base + LUC difference):**
- Source: Community testing and gameplay analysis
- Implemented as `5% + (attacker_LUC - defender_LUC) × 0.2%`, clamped to [0%, 100%]

**Weakness and Crit Multipliers (1.5× each):**
- Source: In-game behavior and community documentation
- Configurable in `config.json` and batch configs

**Note:** Simulator models deterministic baseline formula behavior. It does not include every in-game factor (random variance, level correction, affinities, passives, equipment).

### Understanding Expected Damage

Expected damage = weighted average of normal and crit damage based on crit probability.

**Why it matters:**
- Most realistic damage over many attacks
- Accounts for RNG variation
- Use for DPS comparisons

**Example calculation:**
- Normal damage: 100
- Crit damage: 150
- Crit rate: 10%
- Expected: `100 × 0.9 + 150 × 0.1 = 90 + 15 = 105`

Over 100 attacks, you'd expect ~90 normal hits (9000 damage) + ~10 crits (1500 damage) = 10500 total damage, averaging 105 per hit.

## Practical Examples

### Example 1: Testing Buff Effectiveness

**Question:** Is buffing my STR better than debuffing enemy VIT?

**Config:**
```json
{
  "scenarios": [
    {"name": "Baseline", "attacker_buffs": {}, "defender_buffs": {}},
    {"name": "ATK +3", "attacker_buffs": {"STR": 3}, "defender_buffs": {}},
    {"name": "DEF -3", "attacker_buffs": {}, "defender_buffs": {"VIT": -3}}
  ]
}
```

**Result:**
```
┌─────────────┬──────────┬──────────┐
│ Scenario    │ Normal   │ % Change │
├─────────────┼──────────┼──────────┤
│ Baseline    │     81.8 │    +0.0% │
│ ATK +3      │    130.9 │   +60.0% │
│ DEF -3      │    136.4 │   +66.7% │
└─────────────┴──────────┴──────────┘
```

**Answer:** DEF debuff slightly better (+66.7% vs +60.0%)

**Why:** Debuffing VIT to 0.6× is more effective than buffing STR to 1.6× because damage formula divides by VIT. Lower denominator = bigger impact.

### Example 2: Stacking Buffs and Debuffs

**Question:** How much damage increase from max buffs + debuffs?

**Config:**
```json
{
  "scenarios": [
    {"name": "Baseline", "attacker_buffs": {}, "defender_buffs": {}},
    {"name": "ATK +3 only", "attacker_buffs": {"STR": 3}, "defender_buffs": {}},
    {"name": "DEF -3 only", "attacker_buffs": {}, "defender_buffs": {"VIT": -3}},
    {"name": "Both maxed", "attacker_buffs": {"STR": 3}, "defender_buffs": {"VIT": -3}}
  ]
}
```

**Result:**
```
┌──────────────┬──────────┬──────────┐
│ Scenario     │ Normal   │ % Change │
├──────────────┼──────────┼──────────┤
│ Baseline     │     81.8 │    +0.0% │
│ ATK +3 only  │    130.9 │   +60.0% │
│ DEF -3 only  │    136.4 │   +66.7% │
│ Both maxed   │    218.2 │  +166.7% │
└──────────────┴──────────┴──────────┘
```

**Answer:** 166.7% increase (2.67× multiplier) with both maxed.

**Why:** Buffs multiply: `1.6× STR × (1 / 0.6× VIT) = 2.67× damage`

### Example 3: Comparing Skills

**Question:** Which skill better: 100 power physical or 150 power physical?

**Method:** Run twice with different `skill_power` values:

```json
// First run: skill_power: 100
// Second run: skill_power: 150
```

**Result:** Damage scales linearly with skill power (150 power = 1.5× damage of 100 power).

### Example 4: Finding Optimal Buff Priority

**Question:** With limited buff turns, should I buff STR +3 or STR +2 + LUC +1?

**Config:**
```json
{
  "scenarios": [
    {"name": "Baseline", "attacker_buffs": {}, "defender_buffs": {}},
    {"name": "STR +3", "attacker_buffs": {"STR": 3}, "defender_buffs": {}},
    {"name": "STR +2, LUC +1", "attacker_buffs": {"STR": 2, "LUC": 1}, "defender_buffs": {}}
  ]
}
```

Compare **Expected** column (accounts for crit rate boost from LUC).

**Typical result:** Pure STR usually better unless LUC difference already high.

### Full Example Output

```
================================================================================
SMTV Combat Simulator
================================================================================
Attacker: Nahobino
Defender: Daemon

Baseline damage: 81.8 (normal hit, no weakness)
Crit rate: 6.0%

┌────────────────────────────────────┬───────────┬───────────┬───────────┬───────────┐
│ Scenario                           │ Normal    │ % Change  │ Weakness  │ Expected  │
├────────────────────────────────────┼───────────┼───────────┼───────────┼───────────┤
│ No buffs (baseline)                │      81.8 │     +0.0% │     122.7 │      84.3 │
│ Attacker +3 STR                    │     130.9 │    +60.0% │     196.4 │     134.8 │
│ Defender -3 VIT                    │     136.4 │    +66.7% │     204.5 │     140.5 │
│ Both maxed (+3 STR, -3 VIT)        │     218.2 │   +166.7% │     327.3 │     224.7 │
└────────────────────────────────────┴───────────┴───────────┴───────────┴───────────┘

CSV exported to: output/results.csv
Graphs generated in output/
```

## Troubleshooting

### Virtual environment not activated

**Problem:** `ModuleNotFoundError: No module named 'matplotlib'` after installing requirements.

**Solution:**
```bash
# Make sure virtual environment activated (should see .venv prefix)
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Reinstall if needed
pip install -r requirements.txt
```

### Config file not found

**Problem:** `FileNotFoundError: config.json not found`

**Solution:**
```bash
# Check current directory
pwd

# Should be in project root with config.json
ls config.json

# If in wrong directory, navigate to project root
cd /path/to/smtv-simulator
python3 -m src.runner
```

### Invalid JSON in config

**Problem:** `json.decoder.JSONDecodeError: Expecting ',' delimiter`

**Solution:**
- Remove trailing commas in JSON (not allowed in strict JSON)
- Check matching braces/brackets
- Validate JSON at jsonlint.com
- Common errors:
  ```json
  // WRONG: trailing comma
  {"STR": 3,}
  
  // CORRECT:
  {"STR": 3}
  
  // WRONG: comments not allowed in JSON
  {"STR": 3}  // my comment
  
  // CORRECT: remove comments
  {"STR": 3}
  ```

### Graphs not generating

**Problem:** Graphs missing in `output/` directory.

**Check:**
```bash
# Verify matplotlib installed
pip list | grep matplotlib

# Check output directory exists (created automatically)
ls -la output/

# Run with verbose output
python3 -m src.runner
```

**Common causes:**
- Display backend issues on headless systems (graphs still save as files)
- Permissions issue with `output/` directory
- Matplotlib not installed properly

### Numbers seem wrong

**Problem:** Damage values don't match in-game experience.

**Check:**
1. **Base stats correct?** Verify attacker STR and defender VIT match in-game values
2. **Buff levels correct?** SMTV uses -3 to +3 range (not -4 or higher)
3. **Skill power set?** Default 100, adjust for specific skills
4. **Multipliers match?** Default 1.5× for weakness/crit matches base SMTV

**Note:** Simulator uses simplified formula. In-game damage has variance (±5% random), level differences, and other modifiers not modeled here.

### Permission denied on output directory

**Problem:** `PermissionError: [Errno 13] Permission denied: 'output'`

**Solution:**
```bash
# Check/fix output directory permissions
chmod 755 output/

# Or recreate output directory
rm -rf output/
mkdir output
```

## Testing

Run test suite to verify simulator correctness:

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_combat_engine.py -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

Tests verify:
- Buff application (stat multipliers)
- Damage formulas (base, weakness, crit)
- Crit rate calculation
- Scenario execution
- CSV export format

## Advanced Usage

### Custom Config Files

Create multiple configs for different scenarios:

```bash
# Save different configs
cp config.json configs/endgame_boss.json
cp config.json configs/early_game.json

# Run with specific config
python3 -m src.runner configs/endgame_boss.json
```

### Batch Processing

Run multiple simulations:

```bash
#!/bin/bash
# simulate_all.sh

for config in configs/*.json; do
    echo "Running $config..."
    python3 -m src.runner "$config"
    mv output/results.csv "output/results_$(basename $config .json).csv"
done
```

### Importing Results for Analysis

Python script to compare multiple runs:

```python
import pandas as pd

# Load multiple simulation results
baseline = pd.read_csv('output/baseline_results.csv')
buffed = pd.read_csv('output/buffed_results.csv')

# Filter for expected damage only
baseline_expected = baseline[baseline['hit_type'] == 'expected']
buffed_expected = buffed[buffed['hit_type'] == 'expected']

# Compare
comparison = pd.merge(
    baseline_expected, 
    buffed_expected, 
    on='scenario_name', 
    suffixes=('_baseline', '_buffed')
)
print(comparison[['scenario_name', 'damage_baseline', 'damage_buffed']])
```

### Creating Scenario Templates

Common scenario templates:

**Progressive STR buff test:**
```json
{
  "scenarios": [
    {"name": "Baseline", "attacker_buffs": {}, "defender_buffs": {}},
    {"name": "STR +1", "attacker_buffs": {"STR": 1}, "defender_buffs": {}},
    {"name": "STR +2", "attacker_buffs": {"STR": 2}, "defender_buffs": {}},
    {"name": "STR +3", "attacker_buffs": {"STR": 3}, "defender_buffs": {}}
  ]
}
```

**All-stat buff comparison:**
```json
{
  "scenarios": [
    {"name": "Baseline", "attacker_buffs": {}, "defender_buffs": {}},
    {"name": "Heat Riser", "attacker_buffs": {"STR": 2, "VIT": 2, "AGI": 2}, "defender_buffs": {}},
    {"name": "Luster Candy", "attacker_buffs": {"STR": 2, "VIT": 2, "MAG": 2, "AGI": 2, "LUC": 2}, "defender_buffs": {}},
    {"name": "Debilitate", "attacker_buffs": {}, "defender_buffs": {"STR": -2, "VIT": -2, "MAG": -2, "AGI": -2, "LUC": -2}}
  ]
}
```

## Project Structure

```
smtv-simulator/
├── src/
│   ├── combat_engine.py    # Core damage calculation logic
│   │                       # - Combatant class (stats + buffs)
│   │                       # - CombatEngine class (damage formulas)
│   │                       # - BUFF_MULTIPLIERS constant
│   ├── visualizer.py        # Matplotlib graph generation
│   │                       # - scenario_comparison (bar chart)
│   │                       # - buff_progression (line chart)
│   │                       # - buff_debuff_matrix (heatmap)
│   └── runner.py            # CLI entry point and orchestration
│                           # - Config loading
│                           # - Scenario execution
│                           # - CSV export
│                           # - Terminal output
├── tests/
│   ├── test_combatant.py      # Combatant class tests
│   ├── test_combat_engine.py  # Damage calculation tests
│   └── test_runner.py         # Scenario execution tests
├── config.json              # Main configuration file
├── output/                  # Generated output (created on first run)
│   ├── results.csv
│   ├── scenario_comparison.png
│   ├── buff_progression.png
│   └── buff_debuff_matrix.png
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .venv/                  # Virtual environment (create with python -m venv .venv)
```

## FAQ

### Q: Why is defender -3 VIT more effective than attacker +3 STR?

**A:** Damage formula divides by VIT: `damage = (STR × power) / VIT`

- Buffing STR to 1.6×: `(1.6 × STR) / VIT = 1.6× damage`
- Debuffing VIT to 0.6×: `STR / (0.6 × VIT) = 1.67× damage`

Division by smaller number has bigger impact.

### Q: Can I simulate magic damage?

**A:** Not currently. Simulator focuses on physical damage (STR vs VIT). Magic would use MAG vs VIT formula. Could add in future version.

### Q: Why don't my numbers exactly match in-game?

**A:** Game has additional factors:
- ±5% random variance per hit
- Level difference modifiers
- Affinities (resist/null/drain)
- Equipment passives
- Demon-specific multipliers

Simulator models core buff/debuff mechanics only.

### Q: Do buffs stack multiplicatively?

**A:** No. Each stat has one buff level (-3 to +3). Casting Tarukaja twice = +2 buff, not +1 × +1.

Multiple buffed stats (STR + LUC) affect different parts of formula independently.

### Q: What's difference between Normal and Expected damage?

**A:** 
- **Normal:** Damage if you never crit (deterministic)
- **Expected:** Average damage accounting for crit probability (realistic over many hits)

Use Expected for DPS comparisons.

### Q: How do I test specific in-game skills?

**A:** Set `skill_power` to match skill:
- Lunge: ~80
- Deadly Fury: ~120
- Megaton Press: ~200
- Godly Strike: ~300

Check SMTV wiki for exact values.

### Q: Can I simulate multi-hit skills?

**A:** Not directly. Multiply output damage by number of hits. Note: each hit can crit independently in-game.

### Q: Why is LUC effect so small?

**A:** Each point of LUC only adds 0.2% crit rate. Need large LUC difference for noticeable crit rate change.

Example: 30 LUC difference = only 6% crit rate increase.

### Q: Can I run this without installing Python?

**A:** No, requires Python 3.9+. Python is cross-platform and free to install.

### Q: How do I interpret the heatmap?

**A:** Darker color = higher damage. Find optimal buff/debuff combo by looking at darkest cell. Numbers show exact damage values.

## Performance Notes

- Simulation runs instantly (<1 second for typical configs)
- Graph generation takes 1-2 seconds
- CSV export handles thousands of scenario rows
- No memory issues with reasonable scenario counts (<100 scenarios)

## Future Enhancements

Potential features (not currently implemented):

- Magic damage formulas (MAG vs VIT)
- Elemental affinities (resist/weak/null/drain)
- Multi-hit skill support
- Turn-based battle simulation
- Level difference modifiers
- Equipment/passive effects
- Ailment damage modifiers
- Magatsuhi skill bonuses

## License

MIT

## Credits

Design and implementation assisted by Claude Sonnet 4.5

## Support

For issues or questions:
1. Check Troubleshooting section
2. Verify config.json format
3. Run test suite: `pytest tests/ -v`
4. Check CLAUDE.md for development notes
