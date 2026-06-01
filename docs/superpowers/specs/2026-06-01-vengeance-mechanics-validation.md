# SMTV Vengeance Mechanics Validation - Design Specification

**Date:** 2026-06-01  
**Goal:** Validate DEBUNKED.md claims by implementing complete Shin Megami Tensei V: Vengeance combat mechanics and proving multiplicative synergy dominates over level/stat scaling alone.

---

## Problem Statement

Current simulator uses oversimplified linear damage formulas. DEBUNKED.md argues the "level vs stats" question is a false dichotomy - neither scales infinitely in Vengeance. Real combat driver = multiplicative synergy (stacking Potential × Charge × Crit × Resistance).

**Missing mechanics:**
- Root diminishing returns (Level+10 threshold)
- Level Correction bounds (0.5x floor, 1.5x ceiling)
- 3-tier Vitality damage calculation
- Skill Potential system (-9 to +9)
- Charge state multipliers (1.3x to 3.4x)
- Critical mechanics with Crit Zealot passive
- Stochastic variance (±10%)
- Elemental resistance
- Defense mechanics (Guard, Doubler bug)

---

## Architecture

### Three-Module Structure (Refactor Existing)

```
src/
├── combat_engine.py       # Expand with 8 new calculation layers
├── runner.py              # Add validation mode, scenario suite
└── visualizer.py          # 5 new graphs for validation
```

**Backward compatibility:** Existing configs without new fields use defaults. Current tests pass.

---

## Data Structures

### Combatant Expansion

```python
@dataclass
class Combatant:
    # Existing fields (unchanged)
    name: str
    level: int
    strength: int
    vitality: int
    magic: int
    agility: int
    luck: int
    buffs: Dict[str, int]  # -3 to +3
    
    # New fields
    skill_potentials: Dict[str, int] = field(default_factory=dict)  
        # {"fire": 9, "phys": 4, "ice": 0}
    charge_state: Optional[str] = None  
        # "charge", "concentrate", "impaler_glory", etc.
    passive_abilities: List[str] = field(default_factory=list)  
        # ["critical_zealot", "murderous_glee"]
    guarding: bool = False
    doubler_active: bool = False
```

### New Constants

```python
# Skill Potential → multiplier (DEBUNKED Table in §8)
POTENTIAL_MULTIPLIERS = {
    -9: 0.45, -4: 0.75, 0: 1.0, 
    4: 1.25, 5: 1.35, 9: 1.55
}

# Charge state multipliers (§8)
CHARGE_MULTIPLIERS = {
    "charge": 1.8,
    "concentrate": 1.8,
    "donum_gladi": 1.5,
    "donum_magici": 1.5,
    "impaler_animus": 1.3,
    "impaler_glory": 3.4,
}

# Elemental resistance (§9)
RESISTANCE_MULTIPLIERS = {
    "immune": 0.0,
    "drain": -1.0,
    "repel": -0.5,
    "resist": 0.5,
    "neutral": 1.0,
    "weak": 1.5,
}

# Critical Zealot (§9)
CRIT_ZEALOT_NON_CRIT = 0.9
CRIT_ZEALOT_CRIT = 1.45

# Guard multiplier (§6)
GUARD_MULTIPLIER = 0.8
```

### Config Schema Expansion

```json
{
  "attacker": {
    "level": 99,
    "strength": 109,
    "magic": 109,
    "vitality": 80,
    "agility": 70,
    "luck": 110,
    "buffs": {"attack": 2},
    "skill_potentials": {"phys": 9, "fire": 5},
    "charge_state": "impaler_glory",
    "passive_abilities": ["critical_zealot"]
  },
  "skill": {
    "power": 100,
    "element": "phys",
    "crit_base": 0.05
  },
  "defender": {
    "level": 95,
    "vitality": 80,
    "agility": 60,
    "luck": 64,
    "buffs": {"defense": -2},
    "resistance": "neutral",
    "guarding": false,
    "doubler_active": false
  }
}
```

---

## Damage Calculation Pipeline

### Layer Order (Sequential)

`CombatEngine.calculate_damage()` orchestrates these calls:

1. **Stat Scaling** → `_apply_root_diminishing_returns(stat, level)`
2. **Level Correction** → `_calculate_level_correction(atk_lvl, def_lvl)`
3. **Base Damage** → `_calculate_base_damage(offense, vitality)`
4. **Skill Modifiers** → `_apply_skill_potential()` + `_apply_charge_state()`
5. **Crit Calculation** → `_calculate_crit_rate()` + `_apply_critical_multiplier()`
6. **Resistance** → `_apply_elemental_resistance()`
7. **Passive Abilities** → `_apply_passives()`
8. **Stochastic Variance** → `_apply_variance()`
9. **Defense** → `_apply_guard()` + `_apply_doubler_bug()`

Each layer = isolated method, independently testable.

### Formula Details

**Layer 1: Root Diminishing Returns (DEBUNKED §3)**

```python
def _apply_root_diminishing_returns(self, stat: int, level: int) -> float:
    """Convert raw stat to Offense using Root formula"""
    root = level + 10
    if stat <= root:
        return stat * 2  # Linear phase - full efficiency
    else:
        # Diminishing returns phase
        return root + math.sqrt(stat - root) + root
```

**Layer 2: Level Correction (DEBUNKED §5)**

```python
def _calculate_level_correction(self, attacker_level: int, defender_level: int) -> float:
    """Bounded 0.5x to 1.5x - proof that level doesn't infinitely scale"""
    diff = attacker_level - defender_level
    if abs(diff) <= 2:
        return 1.0  # Near-peer, no penalty/bonus
    
    # Sum Factor calculation
    combined = attacker_level + defender_level
    if combined <= 30:
        sum_factor = 0.0  # Early game - level correction dormant
    elif combined <= 130:
        sum_factor = (combined - 30) / 1000  # Linear ramp
    else:
        sum_factor = 0.1  # Late game - hard cap
    
    correction = 1.0 + (diff * sum_factor)
    # Hard bounds - this is the key constraint
    return max(0.5, min(1.5, correction))
```

**Layer 3: Base Damage - 3-Tier Vitality (DEBUNKED §4)**

```python
def _calculate_base_damage(self, offense: float, vitality: float) -> float:
    """Piecewise function - NOT linear subtraction"""
    diff = offense - vitality
    
    # Tier 1: Heavy mitigation (glancing blow)
    if diff <= offense / 2:
        return (2/3 * offense) - (1/3 * vitality) - (1/3 * math.sqrt(vitality - offense/2))
    
    # Tier 2: Standard penetration (most common)
    elif diff <= 3/4 * offense:
        return offense - vitality
    
    # Tier 3: Overwhelming force
    else:
        return (5/6 * offense) - (1/3 * vitality) + (1/3 * math.sqrt(offense/4 - vitality))
```

**Layer 7: Stochastic Variance (DEBUNKED §12)**

```python
def _apply_variance(self, base_damage: float) -> float:
    """Random ±10% fluctuation - why deterministic sims fail"""
    if base_damage < 10:
        return base_damage
    
    var1 = random.randint(0, int(0.1 * base_damage))
    var2 = random.randint(0, 4)
    return base_damage + var1 + var2
```

**Other layers:** Direct table lookups (Potential, Charge, Resistance) or conditional multipliers (Crit Zealot, Guard, Doubler).

---

## Passive Ability System

**Registry pattern (extensible for GUI later):**

```python
class CombatEngine:
    PASSIVE_EFFECTS = {
        "critical_zealot": lambda state: {
            "damage_mult": 1.45 if state["is_crit"] else 0.9
        },
        "murderous_glee": lambda state: {
            "crit_rate_mult": 2.5
        },
        # Easy to add more passives
    }
    
    def _apply_passives(self, combatant: Combatant, damage_state: dict) -> dict:
        for ability_id in combatant.passive_abilities:
            if ability_id in self.PASSIVE_EFFECTS:
                modifiers = self.PASSIVE_EFFECTS[ability_id](damage_state)
                damage_state.update(modifiers)
        return damage_state
```

**Benefits:**
- Config just lists strings: `"passive_abilities": ["critical_zealot"]`
- Users mix/match any combo
- Future GUI = checkbox list from `PASSIVE_EFFECTS.keys()`
- One agent owns passive system module

---

## Validation Suite

### Scenarios (config/validation/)

6 scenarios prove multiplicative dominance:

1. **overleveled_vs_multiplicative.json**
   - Scenario A: Level 99 vs 85 (1.5x advantage)
   - Scenario B: Level 80 vs 85 (0.5x penalty) + Impaler Glory (3.4x) + Potential +9 (1.55x) + Crit Zealot
   - **Proof:** B > A despite level disadvantage

2. **stat_dumping_vs_root_cap.json**
   - Scenario A: 250 Magic (heavy Root penalty)
   - Scenario B: 109 Magic (Root cap) + multipliers
   - **Proof:** B efficiency > A despite lower raw stat

3. **single_buff_vs_stack.json**
   - Scenario A: Tarukaja only (+20%)
   - Scenario B: Tarukaja + Charge (1.8x) + Potential +5 (1.35x)
   - **Proof:** Multiplicative stack >> single buff

4. **level_scaling_bounds.json**
   - Test full range: Level diff -20 to +20
   - **Proof:** Show 0.5x floor, 1.5x ceiling, near-peer plateau

5. **vitality_tier_transitions.json**
   - Vary Offense/Vitality to hit all 3 tiers
   - **Proof:** Non-linear damage, tier boundaries matter

6. **passive_ability_showcase.json**
   - Critical Zealot on vs off
   - **Proof:** 1.45x multiplier on crit > level advantage

### Runner Implementation

```python
def run_validation_suite(config_path: str, num_trials: int = 100):
    """Run comprehensive validation, capture variance"""
    scenarios = load_all_scenarios(config_path)
    
    results = {}
    for scenario in scenarios:
        damages = []
        for _ in range(num_trials):
            damage = run_scenario(scenario)
            damages.append(damage)
        
        results[scenario.name] = {
            "mean": statistics.mean(damages),
            "std": statistics.stdev(damages),
            "min": min(damages),
            "max": max(damages),
            "config": scenario.config,
        }
    
    return results
```

### CLI

```bash
python3 -m src.runner --validate config/validation/
python3 -m src.runner --validate --trials 1000
python3 -m src.runner --custom my_scenario.json
```

---

## Visualization

### 5 New Graphs

1. **multiplier_breakdown.png** - Stacked bar chart
   - Each bar = one scenario
   - Segments = damage contribution by layer (Base, Level Correction, Potential, Charge, Crit, Passive)
   - **Shows:** Which multipliers matter most

2. **level_vs_multiplicative.png** - Side-by-side grouped bars
   - Group 1: Pure level advantage (90→95→99, 1.0x→1.3x→1.5x)
   - Group 2: Fixed level + increasing multiplier stack
   - **Shows:** Multiplicative overtakes level

3. **root_curve.png** - Line chart
   - X: Raw stat (0-250), Y: Effective Offense
   - Vertical line at Root (Level+10)
   - Two slopes (linear before Root, sqrt after)
   - **Shows:** Diminishing returns proof

4. **vitality_heatmap.png** - 2D color grid
   - X: Offense (0-500), Y: Vitality (0-300)
   - Color = damage tier (red=1, yellow=2, green=3)
   - Annotate tier boundaries
   - **Shows:** Non-linear damage regions

5. **variance_distribution.png** - Histogram + stats
   - 100 trials per scenario
   - Overlay: mean, ±1σ confidence interval
   - **Shows:** Stochastic variance spread (±10%)

### Export Function

```python
def generate_validation_report(results: dict, output_dir: str):
    """Generate all graphs + CSV summary"""
    generate_multiplier_breakdown(results, f"{output_dir}/multiplier_breakdown.png")
    generate_level_vs_multiplicative(results, f"{output_dir}/level_vs_multiplicative.png")
    generate_root_curve(results, f"{output_dir}/root_curve.png")
    generate_vitality_heatmap(results, f"{output_dir}/vitality_heatmap.png")
    generate_variance_distribution(results, f"{output_dir}/variance_dist.png")
    export_summary_table(results, f"{output_dir}/validation_summary.csv")
```

**Output directory:** `output/validation/`

---

## Testing Strategy

### Unit Tests (pytest)

Each layer = isolated test module:

- `test_root_diminishing_returns()` - exact values at key thresholds (109, 120, 160, 250)
- `test_level_correction_bounds()` - verify 0.5x floor, 1.5x ceiling
- `test_vitality_tiers()` - all 3 tiers triggered correctly
- `test_skill_potential()` - lookup table accuracy
- `test_charge_multipliers()` - all charge states
- `test_crit_zealot()` - 0.9x non-crit, 1.45x crit
- `test_stochastic_variance()` - variance within ±10% over 1000 trials
- `test_doubler_bug()` - verify the intentional bug behavior

### Integration Tests

- `test_full_pipeline()` - end-to-end damage calc through all 9 layers
- `test_backward_compat()` - old configs still work with defaults

### Validation Tests

- `test_scenario_suite()` - all 6 validation scenarios run without error
- `test_multiplicative_dominance()` - assertions that scenario B > scenario A in critical comparisons

---

## Implementation Plan Structure

**8 parallel agents (orchestrated via workflow):**

1. **Agent 1:** Core stat scaling (Root formula, Level Correction) → `src/combat_engine.py` layers 1-2
2. **Agent 2:** Vitality system (3-tier calc) → `src/combat_engine.py` layer 3
3. **Agent 3:** Skill modifiers (Potential, Charge) → `src/combat_engine.py` layers 4
4. **Agent 4:** Crit mechanics + resistance → `src/combat_engine.py` layers 5-6
5. **Agent 5:** Passive ability system (registry, Crit Zealot) → `src/combat_engine.py` layer 7
6. **Agent 6:** Defense + variance (Guard, Doubler, stochastic) → `src/combat_engine.py` layers 8-9
7. **Agent 7:** Runner validation mode + scenarios → `src/runner.py` + `config/validation/`
8. **Agent 8:** Visualization suite → `src/visualizer.py` new graphs

**Estimated cost:** 8 agents × ~12k tokens avg = ~96k total tokens  
**Wall time:** ~60-90s (agents run parallel)

---

## Success Criteria

1. **All 6 validation scenarios run successfully**
2. **Multiplicative stack scenarios produce higher damage than pure level/stat scenarios** (proves DEBUNKED claim)
3. **Graphs clearly visualize:**
   - Level Correction bounds (0.5x-1.5x)
   - Root diminishing returns
   - Multiplicative dominance
   - Variance spread
4. **Users can define custom scenarios via JSON** (no code changes needed)
5. **All tests pass** (unit + integration + validation)
6. **Backward compatibility maintained** (existing configs work)

---

## Future Extensions (Out of Scope for Initial Implementation)

- GUI for scenario builder (checkboxes for passives, sliders for stats)
- More passive abilities beyond Crit Zealot
- Enemy AI simulation
- Full turn-based combat sequence
- Press Turn system mechanics
- Magatsuhi skills

---

## References

- DEBUNKED.md (comprehensive formula source)
- Steam Community Guide: Combat Calculation in SMT V: Vengeance
- Reddit discussions on level scaling changes (Vanilla → Vengeance)
