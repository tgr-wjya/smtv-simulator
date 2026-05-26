# SMTV Combat Simulator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a damage calculation simulator to analyze SMTV buff/debuff mechanics through mathematical modeling.

**Architecture:** Core combat engine handles damage formulas and stat calculations. CLI runner orchestrates scenarios from JSON config. Visualizer generates matplotlib graphs. CSV export for external analysis.

**Tech Stack:** Python 3.9+, matplotlib, numpy, dataclasses, pytest

---

## File Structure

```
smtv-simulator/
├── src/
│   ├── __init__.py
│   ├── combat_engine.py       # CombatEngine and Combatant classes
│   ├── visualizer.py           # Matplotlib graph generation
│   └── runner.py               # CLI entry point
├── tests/
│   ├── __init__.py
│   ├── test_combatant.py       # Combatant class tests
│   ├── test_combat_engine.py   # CombatEngine tests
│   └── test_runner.py          # Integration tests
├── config.json                 # Default configuration
├── output/                     # Generated graphs and CSV
├── requirements.txt            # Python dependencies
└── README.md                   # Usage documentation
```

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```txt
matplotlib>=3.5.0
numpy>=1.21.0
pytest>=7.0.0
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.py[cod]
*$py.class
*.so
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
output/*.png
output/*.csv
venv/
.venv/
```

- [ ] **Step 3: Create empty package files**

```bash
touch src/__init__.py tests/__init__.py
```

- [ ] **Step 4: Create output directory**

```bash
mkdir -p output
```

- [ ] **Step 5: Install dependencies**

Run: `python3 -m pip install -r requirements.txt`
Expected: Packages installed successfully

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore src/__init__.py tests/__init__.py
git commit -m "chore: initialize project structure

Set up Python package structure with dependencies:
- matplotlib for graphs
- numpy for calculations
- pytest for testing

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Combatant Class (TDD)

**Files:**
- Create: `tests/test_combatant.py`
- Create: `src/combat_engine.py`

- [ ] **Step 1: Write test for Combatant initialization**

Create `tests/test_combatant.py`:

```python
import pytest
from src.combat_engine import Combatant


def test_combatant_initialization():
    """Test Combatant stores name and stats correctly"""
    stats = {'STR': 45, 'VIT': 38, 'MAG': 42, 'AGI': 40, 'LUC': 35}
    combatant = Combatant(name="Nahobino", base_stats=stats)
    
    assert combatant.name == "Nahobino"
    assert combatant.base_stats['STR'] == 45
    assert combatant.base_stats['VIT'] == 38
    
    # All buff levels should start at 0
    assert combatant.buff_levels['STR'] == 0
    assert combatant.buff_levels['VIT'] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_combatant.py::test_combatant_initialization -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.combat_engine'"

- [ ] **Step 3: Implement Combatant class**

Create `src/combat_engine.py`:

```python
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Combatant:
    """Represents an entity in combat with stats and buff state"""
    name: str
    base_stats: Dict[str, int]
    buff_levels: Dict[str, int] = field(default_factory=lambda: {
        'STR': 0, 'VIT': 0, 'MAG': 0, 'AGI': 0, 'LUC': 0
    })
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_combatant.py::test_combatant_initialization -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_combatant.py src/combat_engine.py
git commit -m "feat: add Combatant class with stats and buff tracking

Combatant stores base stats (STR/VIT/MAG/AGI/LUC) and buff levels
for each stat. Buff levels initialize to 0 (neutral).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 6: Write test for get_effective_stat**

Add to `tests/test_combatant.py`:

```python
def test_get_effective_stat_no_buffs():
    """Test effective stat equals base stat when no buffs"""
    stats = {'STR': 45, 'VIT': 38, 'MAG': 42, 'AGI': 40, 'LUC': 35}
    combatant = Combatant(name="Nahobino", base_stats=stats)
    
    assert combatant.get_effective_stat('STR') == 45.0
    assert combatant.get_effective_stat('VIT') == 38.0


def test_get_effective_stat_with_buffs():
    """Test effective stat applies buff multiplier"""
    stats = {'STR': 100, 'VIT': 100, 'MAG': 100, 'AGI': 100, 'LUC': 100}
    combatant = Combatant(name="Test", base_stats=stats)
    
    # +3 buff = 1.6x multiplier
    combatant.buff_levels['STR'] = 3
    assert combatant.get_effective_stat('STR') == 160.0
    
    # -2 debuff = 0.7x multiplier
    combatant.buff_levels['VIT'] = -2
    assert combatant.get_effective_stat('VIT') == 70.0
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_combatant.py::test_get_effective_stat_no_buffs -v`
Expected: FAIL with "AttributeError: 'Combatant' object has no attribute 'get_effective_stat'"

- [ ] **Step 8: Implement get_effective_stat method**

Add to `src/combat_engine.py` after the Combatant class definition:

```python
# Buff multiplier constants (used by both Combatant and CombatEngine)
BUFF_MULTIPLIERS = {
    -3: 0.6,
    -2: 0.7,
    -1: 0.85,
    0: 1.0,
    1: 1.2,
    2: 1.4,
    3: 1.6
}


@dataclass
class Combatant:
    """Represents an entity in combat with stats and buff state"""
    name: str
    base_stats: Dict[str, int]
    buff_levels: Dict[str, int] = field(default_factory=lambda: {
        'STR': 0, 'VIT': 0, 'MAG': 0, 'AGI': 0, 'LUC': 0
    })
    
    def get_effective_stat(self, stat: str) -> float:
        """Calculate effective stat value with buff multiplier applied"""
        base_value = self.base_stats[stat]
        buff_level = self.buff_levels[stat]
        multiplier = BUFF_MULTIPLIERS[buff_level]
        return base_value * multiplier
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `pytest tests/test_combatant.py::test_get_effective_stat_no_buffs tests/test_combatant.py::test_get_effective_stat_with_buffs -v`
Expected: PASS (both tests)

- [ ] **Step 10: Commit**

```bash
git add tests/test_combatant.py src/combat_engine.py
git commit -m "feat: add get_effective_stat with buff multipliers

Effective stat = base_stat * BUFF_MULTIPLIERS[buff_level]
Multipliers range from 0.6 (-3) to 1.6 (+3).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 11: Write test for apply_buff**

Add to `tests/test_combatant.py`:

```python
def test_apply_buff_increases_level():
    """Test apply_buff increases buff level"""
    stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    combatant = Combatant(name="Test", base_stats=stats)
    
    combatant.apply_buff('STR', 2)
    assert combatant.buff_levels['STR'] == 2
    
    combatant.apply_buff('STR', 1)
    assert combatant.buff_levels['STR'] == 3


def test_apply_buff_caps_at_positive_3():
    """Test buff level cannot exceed +3"""
    stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    combatant = Combatant(name="Test", base_stats=stats)
    
    combatant.apply_buff('STR', 5)
    assert combatant.buff_levels['STR'] == 3


def test_apply_buff_caps_at_negative_3():
    """Test buff level cannot go below -3"""
    stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    combatant = Combatant(name="Test", base_stats=stats)
    
    combatant.apply_buff('VIT', -5)
    assert combatant.buff_levels['VIT'] == -3
```

- [ ] **Step 12: Run test to verify it fails**

Run: `pytest tests/test_combatant.py::test_apply_buff_increases_level -v`
Expected: FAIL with "AttributeError: 'Combatant' object has no attribute 'apply_buff'"

- [ ] **Step 13: Implement apply_buff method**

Add to Combatant class in `src/combat_engine.py`:

```python
    def apply_buff(self, stat: str, delta: int) -> None:
        """
        Apply buff/debuff to a stat. Clamped to [-3, +3].
        
        Args:
            stat: Stat name ('STR', 'VIT', etc.)
            delta: Change amount (positive = buff, negative = debuff)
        """
        new_level = self.buff_levels[stat] + delta
        self.buff_levels[stat] = max(-3, min(3, new_level))
```

- [ ] **Step 14: Run tests to verify they pass**

Run: `pytest tests/test_combatant.py::test_apply_buff_increases_level tests/test_combatant.py::test_apply_buff_caps_at_positive_3 tests/test_combatant.py::test_apply_buff_caps_at_negative_3 -v`
Expected: PASS (all tests)

- [ ] **Step 15: Commit**

```bash
git add tests/test_combatant.py src/combat_engine.py
git commit -m "feat: add apply_buff with clamping to [-3, +3]

apply_buff modifies buff_levels by delta, clamped to valid range.
Prevents overflow beyond SMTV's buff limits.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 16: Write test for apply_all_buffs**

Add to `tests/test_combatant.py`:

```python
def test_apply_all_buffs():
    """Test apply_all_buffs affects all stats"""
    stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    combatant = Combatant(name="Test", base_stats=stats)
    
    combatant.apply_all_buffs(2)
    
    assert combatant.buff_levels['STR'] == 2
    assert combatant.buff_levels['VIT'] == 2
    assert combatant.buff_levels['MAG'] == 2
    assert combatant.buff_levels['AGI'] == 2
    assert combatant.buff_levels['LUC'] == 2


def test_apply_all_buffs_respects_individual_caps():
    """Test apply_all_buffs clamps each stat independently"""
    stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    combatant = Combatant(name="Test", base_stats=stats)
    
    # Pre-buff STR to +2
    combatant.buff_levels['STR'] = 2
    
    # Apply +2 to all (STR should cap at +3, others at +2)
    combatant.apply_all_buffs(2)
    
    assert combatant.buff_levels['STR'] == 3
    assert combatant.buff_levels['VIT'] == 2
```

- [ ] **Step 17: Run test to verify it fails**

Run: `pytest tests/test_combatant.py::test_apply_all_buffs -v`
Expected: FAIL with "AttributeError: 'Combatant' object has no attribute 'apply_all_buffs'"

- [ ] **Step 18: Implement apply_all_buffs method**

Add to Combatant class in `src/combat_engine.py`:

```python
    def apply_all_buffs(self, delta: int) -> None:
        """
        Apply same buff/debuff to all stats.
        
        Args:
            delta: Change amount (positive = buff, negative = debuff)
        """
        for stat in self.buff_levels.keys():
            self.apply_buff(stat, delta)
```

- [ ] **Step 19: Run tests to verify they pass**

Run: `pytest tests/test_combatant.py::test_apply_all_buffs tests/test_combatant.py::test_apply_all_buffs_respects_individual_caps -v`
Expected: PASS (both tests)

- [ ] **Step 20: Commit**

```bash
git add tests/test_combatant.py src/combat_engine.py
git commit -m "feat: add apply_all_buffs for group stat changes

Apply same delta to all stats, each clamped independently.
Supports Luster Candy / Debilitate mechanics.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: CombatEngine Base Damage (TDD)

**Files:**
- Create: `tests/test_combat_engine.py`
- Modify: `src/combat_engine.py`

- [ ] **Step 1: Write test for CombatEngine initialization**

Create `tests/test_combat_engine.py`:

```python
import pytest
from src.combat_engine import CombatEngine, Combatant


def test_combat_engine_initialization():
    """Test CombatEngine stores formula parameters"""
    engine = CombatEngine(
        weakness_mult=1.5,
        crit_mult=1.5,
        skill_power=100
    )
    
    assert engine.weakness_multiplier == 1.5
    assert engine.crit_multiplier == 1.5
    assert engine.skill_power == 100


def test_combat_engine_default_values():
    """Test CombatEngine uses sensible defaults"""
    engine = CombatEngine()
    
    assert engine.weakness_multiplier == 1.5
    assert engine.crit_multiplier == 1.5
    assert engine.skill_power == 100
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_combat_engine.py::test_combat_engine_initialization -v`
Expected: FAIL with "cannot import name 'CombatEngine'"

- [ ] **Step 3: Implement CombatEngine class**

Add to `src/combat_engine.py` after Combatant class:

```python
class CombatEngine:
    """Handles damage calculation with SMTV formulas"""
    
    def __init__(
        self,
        weakness_mult: float = 1.5,
        crit_mult: float = 1.5,
        skill_power: int = 100
    ):
        self.weakness_multiplier = weakness_mult
        self.crit_multiplier = crit_mult
        self.skill_power = skill_power
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_combat_engine.py::test_combat_engine_initialization tests/test_combat_engine.py::test_combat_engine_default_values -v`
Expected: PASS (both tests)

- [ ] **Step 5: Commit**

```bash
git add tests/test_combat_engine.py src/combat_engine.py
git commit -m "feat: add CombatEngine with formula parameters

CombatEngine stores weakness multiplier, crit multiplier, and
skill power. Defaults match SMTV values.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 6: Write test for calculate_base_damage**

Add to `tests/test_combat_engine.py`:

```python
def test_calculate_base_damage_no_buffs():
    """Test base damage formula: (STR * skill_power) / VIT"""
    engine = CombatEngine(skill_power=100)
    
    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    damage = engine.calculate_base_damage(attacker, defender)
    
    # (50 * 100) / 50 = 100
    assert damage == 100.0


def test_calculate_base_damage_with_buffs():
    """Test base damage uses effective stats (with buffs)"""
    engine = CombatEngine(skill_power=100)
    
    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    # Attacker +3 STR (1.6x), Defender -2 VIT (0.7x)
    attacker.buff_levels['STR'] = 3
    defender.buff_levels['VIT'] = -2
    
    damage = engine.calculate_base_damage(attacker, defender)
    
    # (50 * 1.6 * 100) / (50 * 0.7) = 8000 / 35 = 228.57...
    assert abs(damage - 228.57) < 0.01
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_combat_engine.py::test_calculate_base_damage_no_buffs -v`
Expected: FAIL with "AttributeError: 'CombatEngine' object has no attribute 'calculate_base_damage'"

- [ ] **Step 8: Implement calculate_base_damage method**

Add to CombatEngine class in `src/combat_engine.py`:

```python
    def calculate_base_damage(
        self,
        attacker: Combatant,
        defender: Combatant
    ) -> float:
        """
        Calculate base physical damage.
        
        Formula: (effective_STR * skill_power) / effective_VIT
        
        Args:
            attacker: Attacking combatant
            defender: Defending combatant
            
        Returns:
            Base damage (before weakness/crit)
        """
        effective_str = attacker.get_effective_stat('STR')
        effective_vit = defender.get_effective_stat('VIT')
        
        damage = (effective_str * self.skill_power) / effective_vit
        return damage
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `pytest tests/test_combat_engine.py::test_calculate_base_damage_no_buffs tests/test_combat_engine.py::test_calculate_base_damage_with_buffs -v`
Expected: PASS (both tests)

- [ ] **Step 10: Commit**

```bash
git add tests/test_combat_engine.py src/combat_engine.py
git commit -m "feat: add calculate_base_damage with buff support

Base damage = (effective_STR * skill_power) / effective_VIT
Uses get_effective_stat to apply buff multipliers.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: CombatEngine Critical Hits (TDD)

**Files:**
- Modify: `tests/test_combat_engine.py`
- Modify: `src/combat_engine.py`

- [ ] **Step 1: Write test for calculate_crit_rate**

Add to `tests/test_combat_engine.py`:

```python
def test_calculate_crit_rate_equal_luck():
    """Test crit rate when attacker and defender have equal LUC"""
    engine = CombatEngine()
    
    stats_a = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    stats_d = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    
    attacker = Combatant(name="Attacker", base_stats=stats_a)
    defender = Combatant(name="Defender", base_stats=stats_d)
    
    crit_rate = engine.calculate_crit_rate(attacker, defender)
    
    # Base crit rate when LUC difference is 0
    assert crit_rate == 0.05


def test_calculate_crit_rate_higher_luck():
    """Test crit rate increases with attacker LUC advantage"""
    engine = CombatEngine()
    
    stats_a = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 60}
    stats_d = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 40}
    
    attacker = Combatant(name="Attacker", base_stats=stats_a)
    defender = Combatant(name="Defender", base_stats=stats_d)
    
    crit_rate = engine.calculate_crit_rate(attacker, defender)
    
    # +20 LUC difference = 5% base + (20 * 0.002) = 9%
    assert abs(crit_rate - 0.09) < 0.001


def test_calculate_crit_rate_lower_luck():
    """Test crit rate decreases with attacker LUC disadvantage"""
    engine = CombatEngine()
    
    stats_a = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 30}
    stats_d = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    
    attacker = Combatant(name="Attacker", base_stats=stats_a)
    defender = Combatant(name="Defender", base_stats=stats_d)
    
    crit_rate = engine.calculate_crit_rate(attacker, defender)
    
    # -20 LUC difference = 5% base + (20 * -0.002) = 1%
    assert abs(crit_rate - 0.01) < 0.001


def test_calculate_crit_rate_with_luck_buffs():
    """Test crit rate uses effective LUC (with buffs)"""
    engine = CombatEngine()
    
    stats_a = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    stats_d = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    
    attacker = Combatant(name="Attacker", base_stats=stats_a)
    defender = Combatant(name="Defender", base_stats=stats_d)
    
    # Attacker +3 LUC (1.6x = 80), defender -1 LUC (0.85x = 42.5)
    attacker.buff_levels['LUC'] = 3
    defender.buff_levels['LUC'] = -1
    
    crit_rate = engine.calculate_crit_rate(attacker, defender)
    
    # Difference: 80 - 42.5 = 37.5
    # Crit rate: 5% + (37.5 * 0.002) = 5% + 7.5% = 12.5%
    assert abs(crit_rate - 0.125) < 0.001


def test_calculate_crit_rate_caps_at_100_percent():
    """Test crit rate cannot exceed 100%"""
    engine = CombatEngine()
    
    stats_a = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 200}
    stats_d = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 10}
    
    attacker = Combatant(name="Attacker", base_stats=stats_a)
    defender = Combatant(name="Defender", base_stats=stats_d)
    
    crit_rate = engine.calculate_crit_rate(attacker, defender)
    
    assert crit_rate <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_combat_engine.py::test_calculate_crit_rate_equal_luck -v`
Expected: FAIL with "AttributeError: 'CombatEngine' object has no attribute 'calculate_crit_rate'"

- [ ] **Step 3: Implement calculate_crit_rate method**

Add to CombatEngine class in `src/combat_engine.py`:

```python
    def calculate_crit_rate(
        self,
        attacker: Combatant,
        defender: Combatant
    ) -> float:
        """
        Calculate critical hit rate based on LUC difference.
        
        Formula: 5% base + (attacker_LUC - defender_LUC) * 0.2%
        Capped at 100%.
        
        Args:
            attacker: Attacking combatant
            defender: Defending combatant
            
        Returns:
            Crit rate as decimal (0.0 to 1.0)
        """
        attacker_luc = attacker.get_effective_stat('LUC')
        defender_luc = defender.get_effective_stat('LUC')
        
        luc_difference = attacker_luc - defender_luc
        crit_rate = 0.05 + (luc_difference * 0.002)
        
        return min(1.0, max(0.0, crit_rate))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_combat_engine.py -k calculate_crit_rate -v`
Expected: PASS (all crit_rate tests)

- [ ] **Step 5: Commit**

```bash
git add tests/test_combat_engine.py src/combat_engine.py
git commit -m "feat: add calculate_crit_rate based on LUC difference

Crit rate = 5% base + (LUC_diff * 0.2%), capped at 100%.
Uses effective LUC (respects buffs).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: CombatEngine Full Damage Calculation (TDD)

**Files:**
- Modify: `tests/test_combat_engine.py`
- Modify: `src/combat_engine.py`

- [ ] **Step 1: Write test for calculate_damage (no modifiers)**

Add to `tests/test_combat_engine.py`:

```python
def test_calculate_damage_normal():
    """Test calculate_damage with no weakness or crit"""
    engine = CombatEngine(skill_power=100)
    
    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    damage = engine.calculate_damage(
        attacker, defender,
        is_weakness=False,
        is_crit=False
    )
    
    # Base damage only: (50 * 100) / 50 = 100
    assert damage == 100.0
```

- [ ] **Step 2: Write test for calculate_damage (weakness only)**

Add to `tests/test_combat_engine.py`:

```python
def test_calculate_damage_weakness():
    """Test calculate_damage applies weakness multiplier"""
    engine = CombatEngine(skill_power=100, weakness_mult=1.5)
    
    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    damage = engine.calculate_damage(
        attacker, defender,
        is_weakness=True,
        is_crit=False
    )
    
    # Base (100) * weakness (1.5) = 150
    assert damage == 150.0
```

- [ ] **Step 3: Write test for calculate_damage (crit only)**

Add to `tests/test_combat_engine.py`:

```python
def test_calculate_damage_crit():
    """Test calculate_damage applies crit multiplier"""
    engine = CombatEngine(skill_power=100, crit_mult=1.5)
    
    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    damage = engine.calculate_damage(
        attacker, defender,
        is_weakness=False,
        is_crit=True
    )
    
    # Base (100) * crit (1.5) = 150
    assert damage == 150.0
```

- [ ] **Step 4: Write test for calculate_damage (weakness + crit)**

Add to `tests/test_combat_engine.py`:

```python
def test_calculate_damage_weakness_and_crit():
    """Test calculate_damage stacks weakness and crit multipliers"""
    engine = CombatEngine(skill_power=100, weakness_mult=1.5, crit_mult=1.5)
    
    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    damage = engine.calculate_damage(
        attacker, defender,
        is_weakness=True,
        is_crit=True
    )
    
    # Base (100) * weakness (1.5) * crit (1.5) = 225
    assert damage == 225.0
```

- [ ] **Step 5: Run test to verify it fails**

Run: `pytest tests/test_combat_engine.py::test_calculate_damage_normal -v`
Expected: FAIL with "AttributeError: 'CombatEngine' object has no attribute 'calculate_damage'"

- [ ] **Step 6: Implement calculate_damage method**

Add to CombatEngine class in `src/combat_engine.py`:

```python
    def calculate_damage(
        self,
        attacker: Combatant,
        defender: Combatant,
        is_weakness: bool = False,
        is_crit: bool = False
    ) -> float:
        """
        Calculate full damage with optional weakness/crit modifiers.
        
        Order: base_damage -> weakness mult -> crit mult
        
        Args:
            attacker: Attacking combatant
            defender: Defending combatant
            is_weakness: Apply weakness multiplier if True
            is_crit: Apply crit multiplier if True
            
        Returns:
            Final damage
        """
        damage = self.calculate_base_damage(attacker, defender)
        
        if is_weakness:
            damage *= self.weakness_multiplier
        
        if is_crit:
            damage *= self.crit_multiplier
        
        return damage
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `pytest tests/test_combat_engine.py -k calculate_damage -v`
Expected: PASS (all calculate_damage tests)

- [ ] **Step 8: Commit**

```bash
git add tests/test_combat_engine.py src/combat_engine.py
git commit -m "feat: add calculate_damage with weakness and crit

Calculates full damage: base -> weakness mult -> crit mult.
Multipliers stack multiplicatively.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 9: Write test for calculate_expected_damage**

Add to `tests/test_combat_engine.py`:

```python
def test_calculate_expected_damage():
    """Test expected damage weights by crit rate"""
    engine = CombatEngine(skill_power=100, crit_mult=2.0)
    
    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 50}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 50}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    expected = engine.calculate_expected_damage(
        attacker, defender,
        is_weakness=False
    )
    
    # Crit rate = 5% (equal LUC)
    # Base damage = 100, crit damage = 200
    # Expected = 100 * 0.95 + 200 * 0.05 = 95 + 10 = 105
    assert abs(expected - 105.0) < 0.01


def test_calculate_expected_damage_with_weakness():
    """Test expected damage with weakness accounts for crit on weakness hit"""
    engine = CombatEngine(skill_power=100, weakness_mult=1.5, crit_mult=2.0)
    
    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 50}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 50}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    expected = engine.calculate_expected_damage(
        attacker, defender,
        is_weakness=True
    )
    
    # Crit rate = 5%
    # Weakness damage = 150, weakness+crit damage = 300
    # Expected = 150 * 0.95 + 300 * 0.05 = 142.5 + 15 = 157.5
    assert abs(expected - 157.5) < 0.01
```

- [ ] **Step 10: Run test to verify it fails**

Run: `pytest tests/test_combat_engine.py::test_calculate_expected_damage -v`
Expected: FAIL with "AttributeError: 'CombatEngine' object has no attribute 'calculate_expected_damage'"

- [ ] **Step 11: Implement calculate_expected_damage method**

Add to CombatEngine class in `src/combat_engine.py`:

```python
    def calculate_expected_damage(
        self,
        attacker: Combatant,
        defender: Combatant,
        is_weakness: bool = False
    ) -> float:
        """
        Calculate expected damage accounting for crit probability.
        
        Expected = normal_dmg * (1 - crit_rate) + crit_dmg * crit_rate
        
        Args:
            attacker: Attacking combatant
            defender: Defending combatant
            is_weakness: Apply weakness multiplier if True
            
        Returns:
            Expected damage value
        """
        crit_rate = self.calculate_crit_rate(attacker, defender)
        
        normal_damage = self.calculate_damage(
            attacker, defender,
            is_weakness=is_weakness,
            is_crit=False
        )
        
        crit_damage = self.calculate_damage(
            attacker, defender,
            is_weakness=is_weakness,
            is_crit=True
        )
        
        expected = normal_damage * (1 - crit_rate) + crit_damage * crit_rate
        return expected
```

- [ ] **Step 12: Run tests to verify they pass**

Run: `pytest tests/test_combat_engine.py::test_calculate_expected_damage tests/test_combat_engine.py::test_calculate_expected_damage_with_weakness -v`
Expected: PASS (both tests)

- [ ] **Step 13: Commit**

```bash
git add tests/test_combat_engine.py src/combat_engine.py
git commit -m "feat: add calculate_expected_damage with crit weighting

Expected damage = normal * (1 - crit_rate) + crit * crit_rate.
Accounts for probabilistic crit occurrence.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Configuration File

**Files:**
- Create: `config.json`

- [ ] **Step 1: Create config.json with example data**

Create `config.json`:

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

- [ ] **Step 2: Commit**

```bash
git add config.json
git commit -m "feat: add default config with example scenarios

Config includes attacker/defender stats, 7 test scenarios
(baseline, buffs only, debuffs only, combined), and formula
parameters.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Runner - Config Loading (TDD)

**Files:**
- Create: `tests/test_runner.py`
- Create: `src/runner.py`

- [ ] **Step 1: Write test for load_config**

Create `tests/test_runner.py`:

```python
import pytest
import json
import tempfile
import os
from src.runner import load_config


def test_load_config():
    """Test load_config reads JSON correctly"""
    config_data = {
        "attacker": {
            "name": "Test",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "defender": {
            "name": "Enemy",
            "stats": {"STR": 40, "VIT": 40, "MAG": 40, "AGI": 40, "LUC": 40}
        },
        "scenarios": [
            {"name": "Test", "attacker_buffs": {}, "defender_buffs": {}}
        ],
        "formulas": {
            "weakness_multiplier": 1.5,
            "crit_multiplier": 1.5,
            "skill_power": 100
        }
    }
    
    # Write temp config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name
    
    try:
        config = load_config(temp_path)
        
        assert config['attacker']['name'] == "Test"
        assert config['attacker']['stats']['STR'] == 50
        assert config['defender']['name'] == "Enemy"
        assert len(config['scenarios']) == 1
        assert config['formulas']['weakness_multiplier'] == 1.5
    finally:
        os.unlink(temp_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_runner.py::test_load_config -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.runner'"

- [ ] **Step 3: Implement load_config function**

Create `src/runner.py`:

```python
import json
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to config JSON file
        
    Returns:
        Parsed config dictionary
    """
    with open(config_path, 'r') as f:
        return json.load(f)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_runner.py::test_load_config -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_runner.py src/runner.py
git commit -m "feat: add load_config to read JSON configuration

Loads attacker/defender stats, scenarios, and formula parameters
from JSON file.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Runner - Scenario Execution (TDD)

**Files:**
- Modify: `tests/test_runner.py`
- Modify: `src/runner.py`

- [ ] **Step 1: Write test for run_scenario**

Add to `tests/test_runner.py`:

```python
from src.runner import run_scenario
from src.combat_engine import CombatEngine, Combatant


def test_run_scenario_no_buffs():
    """Test run_scenario with baseline (no buffs)"""
    engine = CombatEngine(skill_power=100, weakness_mult=1.5, crit_mult=1.5)
    
    attacker_stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    defender_stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    scenario = {
        "name": "No buffs",
        "attacker_buffs": {},
        "defender_buffs": {}
    }
    
    result = run_scenario(engine, attacker, defender, scenario)
    
    assert result['scenario_name'] == "No buffs"
    assert result['damages']['normal'] == 100.0
    assert result['damages']['normal_weakness'] == 150.0
    assert result['damages']['crit'] == 150.0
    assert result['damages']['crit_weakness'] == 225.0
    assert abs(result['crit_rate'] - 0.05) < 0.001


def test_run_scenario_with_buffs():
    """Test run_scenario applies buffs from scenario config"""
    engine = CombatEngine(skill_power=100, weakness_mult=1.5, crit_mult=1.5)
    
    attacker_stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    defender_stats = {'STR': 50, 'VIT': 50, 'MAG': 50, 'AGI': 50, 'LUC': 50}
    
    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)
    
    scenario = {
        "name": "Buffs test",
        "attacker_buffs": {"STR": 3},
        "defender_buffs": {"VIT": -2}
    }
    
    result = run_scenario(engine, attacker, defender, scenario)
    
    # STR: 50 * 1.6 = 80, VIT: 50 * 0.7 = 35
    # Base damage: (80 * 100) / 35 = 228.57...
    assert abs(result['damages']['normal'] - 228.57) < 0.01
    
    # Buffs should be reset after scenario
    assert attacker.buff_levels['STR'] == 0
    assert defender.buff_levels['VIT'] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_runner.py::test_run_scenario_no_buffs -v`
Expected: FAIL with "cannot import name 'run_scenario'"

- [ ] **Step 3: Implement run_scenario function**

Add to `src/runner.py`:

```python
from src.combat_engine import CombatEngine, Combatant
from typing import Dict, Any
from copy import deepcopy


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_runner.py::test_run_scenario_no_buffs tests/test_runner.py::test_run_scenario_with_buffs -v`
Expected: PASS (both tests)

- [ ] **Step 5: Commit**

```bash
git add tests/test_runner.py src/runner.py
git commit -m "feat: add run_scenario to execute combat scenarios

Applies scenario buffs, calculates all damage variants (normal,
weakness, crit, expected), then resets buffs.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 6: Write test for run_all_scenarios**

Add to `tests/test_runner.py`:

```python
from src.runner import run_all_scenarios


def test_run_all_scenarios():
    """Test run_all_scenarios processes all scenarios from config"""
    config = {
        "attacker": {
            "name": "Attacker",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "defender": {
            "name": "Defender",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "scenarios": [
            {"name": "Scenario 1", "attacker_buffs": {}, "defender_buffs": {}},
            {"name": "Scenario 2", "attacker_buffs": {"STR": 2}, "defender_buffs": {}}
        ],
        "formulas": {
            "weakness_multiplier": 1.5,
            "crit_multiplier": 1.5,
            "skill_power": 100
        }
    }
    
    results = run_all_scenarios(config)
    
    assert len(results) == 2
    assert results[0]['scenario_name'] == "Scenario 1"
    assert results[1]['scenario_name'] == "Scenario 2"
    
    # First scenario (baseline) should have percent_change = 0
    assert results[0]['percent_change'] == 0.0
    
    # Second scenario should show % increase
    assert results[1]['percent_change'] > 0


def test_run_all_scenarios_calculates_percent_change():
    """Test percent_change is calculated relative to baseline"""
    config = {
        "attacker": {
            "name": "Attacker",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "defender": {
            "name": "Defender",
            "stats": {"STR": 50, "VIT": 50, "MAG": 50, "AGI": 50, "LUC": 50}
        },
        "scenarios": [
            {"name": "Baseline", "attacker_buffs": {}, "defender_buffs": {}},
            {"name": "+3 STR", "attacker_buffs": {"STR": 3}, "defender_buffs": {}}
        ],
        "formulas": {
            "weakness_multiplier": 1.5,
            "crit_multiplier": 1.5,
            "skill_power": 100
        }
    }
    
    results = run_all_scenarios(config)
    
    baseline_damage = results[0]['damages']['normal']
    buffed_damage = results[1]['damages']['normal']
    
    expected_percent_change = ((buffed_damage - baseline_damage) / baseline_damage) * 100
    
    assert abs(results[1]['percent_change'] - expected_percent_change) < 0.01
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_runner.py::test_run_all_scenarios -v`
Expected: FAIL with "cannot import name 'run_all_scenarios'"

- [ ] **Step 8: Implement run_all_scenarios function**

Add to `src/runner.py`:

```python
from typing import List


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
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `pytest tests/test_runner.py::test_run_all_scenarios tests/test_runner.py::test_run_all_scenarios_calculates_percent_change -v`
Expected: PASS (both tests)

- [ ] **Step 10: Commit**

```bash
git add tests/test_runner.py src/runner.py
git commit -m "feat: add run_all_scenarios with percent change tracking

Processes all scenarios from config, calculates percent change
relative to baseline (first scenario).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Runner - Output Formatting

**Files:**
- Modify: `src/runner.py`

- [ ] **Step 1: Implement print_table function**

Add to `src/runner.py`:

```python
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
```

- [ ] **Step 2: Test print_table manually**

Run: `python3 -c "
from src.runner import run_all_scenarios, print_table, load_config
config = load_config('config.json')
results = run_all_scenarios(config)
print_table(results, config['attacker']['name'], config['defender']['name'])
"`

Expected: Formatted ASCII table displayed in terminal

- [ ] **Step 3: Commit**

```bash
git add src/runner.py
git commit -m "feat: add print_table for ASCII output

Displays formatted table with scenario names, damage values,
percent change, and weakness damage.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Runner - CSV Export

**Files:**
- Modify: `src/runner.py`

- [ ] **Step 1: Implement export_csv function**

Add to `src/runner.py`:

```python
import csv
import os


def export_csv(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export scenario results to CSV file.
    
    Args:
        results: List of scenario results from run_all_scenarios
        output_path: Path to output CSV file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = [
            'scenario_name',
            'attacker_STR_buff', 'attacker_VIT_buff', 'attacker_MAG_buff',
            'attacker_AGI_buff', 'attacker_LUC_buff',
            'defender_STR_buff', 'defender_VIT_buff', 'defender_MAG_buff',
            'defender_AGI_buff', 'defender_LUC_buff',
            'hit_type', 'weakness', 'crit',
            'damage', 'crit_rate', 'percent_change', 'baseline_damage'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        baseline_damage = results[0]['damages']['normal'] if results else 0
        
        for result in results:
            scenario_name = result['scenario_name']
            attacker_buffs = result['attacker_buffs']
            defender_buffs = result['defender_buffs']
            crit_rate = result['crit_rate']
            percent_change = result['percent_change']
            
            # Helper to get buff level (default 0)
            def get_buff(buffs_dict, stat):
                return buffs_dict.get(stat, 0)
            
            # Common row data
            common_data = {
                'scenario_name': scenario_name,
                'attacker_STR_buff': get_buff(attacker_buffs, 'STR'),
                'attacker_VIT_buff': get_buff(attacker_buffs, 'VIT'),
                'attacker_MAG_buff': get_buff(attacker_buffs, 'MAG'),
                'attacker_AGI_buff': get_buff(attacker_buffs, 'AGI'),
                'attacker_LUC_buff': get_buff(attacker_buffs, 'LUC'),
                'defender_STR_buff': get_buff(defender_buffs, 'STR'),
                'defender_VIT_buff': get_buff(defender_buffs, 'VIT'),
                'defender_MAG_buff': get_buff(defender_buffs, 'MAG'),
                'defender_AGI_buff': get_buff(defender_buffs, 'AGI'),
                'defender_LUC_buff': get_buff(defender_buffs, 'LUC'),
                'crit_rate': crit_rate,
                'percent_change': percent_change,
                'baseline_damage': baseline_damage
            }
            
            # Write rows for each damage variant
            damage_variants = [
                ('normal', False, False, result['damages']['normal']),
                ('normal_weakness', True, False, result['damages']['normal_weakness']),
                ('crit', False, True, result['damages']['crit']),
                ('crit_weakness', True, True, result['damages']['crit_weakness']),
                ('expected', False, False, result['damages']['expected']),
                ('expected_weakness', True, False, result['damages']['expected_weakness'])
            ]
            
            for hit_type, weakness, crit, damage in damage_variants:
                row = {
                    **common_data,
                    'hit_type': hit_type,
                    'weakness': weakness,
                    'crit': crit,
                    'damage': damage
                }
                writer.writerow(row)
    
    print(f"CSV exported to: {output_path}")
```

- [ ] **Step 2: Test export_csv**

Run: `python3 -c "
from src.runner import run_all_scenarios, export_csv, load_config
config = load_config('config.json')
results = run_all_scenarios(config)
export_csv(results, 'output/test_results.csv')
"`

Expected: CSV file created at output/test_results.csv

- [ ] **Step 3: Verify CSV content**

Run: `head -n 5 output/test_results.csv`
Expected: Header row + data rows visible

- [ ] **Step 4: Commit**

```bash
git add src/runner.py
git commit -m "feat: add export_csv for detailed results

Exports one row per damage variant (normal, weakness, crit, etc)
with all buff levels and percent change. Output to output/ dir.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Visualizer - Scenario Comparison Bar Chart

**Files:**
- Create: `src/visualizer.py`

- [ ] **Step 1: Implement generate_scenario_comparison**

Create `src/visualizer.py`:

```python
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any
import os


def generate_scenario_comparison(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generate bar chart comparing damage across scenarios.
    
    Args:
        results: List of scenario results
        output_path: Path to save PNG file
    """
    if not results:
        print("No results to visualize")
        return
    
    scenario_names = [r['scenario_name'] for r in results]
    normal_damages = [r['damages']['normal'] for r in results]
    weakness_damages = [r['damages']['normal_weakness'] for r in results]
    crit_damages = [r['damages']['crit'] for r in results]
    crit_weakness_damages = [r['damages']['crit_weakness'] for r in results]
    percent_changes = [r['percent_change'] for r in results]
    
    x = np.arange(len(scenario_names))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot grouped bars
    rects1 = ax.bar(x - 1.5*width, normal_damages, width, label='Normal')
    rects2 = ax.bar(x - 0.5*width, weakness_damages, width, label='Weakness')
    rects3 = ax.bar(x + 0.5*width, crit_damages, width, label='Crit')
    rects4 = ax.bar(x + 1.5*width, crit_weakness_damages, width, label='Crit + Weakness')
    
    # Add percent change labels above normal damage bars
    for i, (rect, pct) in enumerate(zip(rects1, percent_changes)):
        height = rect.get_height()
        label = f"+{pct:.1f}%" if pct >= 0 else f"{pct:.1f}%"
        ax.text(rect.get_x() + rect.get_width()/2., height,
                label, ha='center', va='bottom', fontsize=8, rotation=45)
    
    ax.set_xlabel('Scenario', fontsize=12)
    ax.set_ylabel('Damage', fontsize=12)
    ax.set_title('Damage Comparison Across Scenarios', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"Scenario comparison chart saved to: {output_path}")
```

- [ ] **Step 2: Test generate_scenario_comparison**

Run: `python3 -c "
from src.runner import run_all_scenarios, load_config
from src.visualizer import generate_scenario_comparison
config = load_config('config.json')
results = run_all_scenarios(config)
generate_scenario_comparison(results, 'output/scenario_comparison.png')
"`

Expected: PNG file created at output/scenario_comparison.png

- [ ] **Step 3: View generated image**

Run: `ls -lh output/scenario_comparison.png`
Expected: File exists with reasonable size (~50-200KB)

- [ ] **Step 4: Commit**

```bash
git add src/visualizer.py
git commit -m "feat: add generate_scenario_comparison bar chart

Grouped bar chart showing normal, weakness, crit, and crit+weakness
damage per scenario. Percent change labels above normal bars.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Visualizer - Progressive Buff Line Chart

**Files:**
- Modify: `src/visualizer.py`

- [ ] **Step 1: Implement generate_progressive_buff_chart**

Add to `src/visualizer.py`:

```python
from src.combat_engine import CombatEngine, Combatant


def generate_progressive_buff_chart(
    engine: CombatEngine,
    attacker: Combatant,
    defender: Combatant,
    output_path: str
) -> None:
    """
    Generate line chart showing damage as attacker buffs increase.
    
    Shows multiple lines for different defender debuff levels.
    
    Args:
        engine: CombatEngine instance
        attacker: Attacker combatant (at base buffs)
        defender: Defender combatant (at base buffs)
        output_path: Path to save PNG file
    """
    buff_levels = list(range(-3, 4))  # -3 to +3
    defender_debuff_levels = [0, -1, -2, -3]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for defender_debuff in defender_debuff_levels:
        damages = []
        
        for attacker_buff in buff_levels:
            # Set buffs
            attacker.buff_levels['STR'] = attacker_buff
            defender.buff_levels['VIT'] = defender_debuff
            
            # Calculate damage
            damage = engine.calculate_damage(attacker, defender, is_weakness=False, is_crit=False)
            damages.append(damage)
        
        # Reset buffs
        attacker.buff_levels['STR'] = 0
        defender.buff_levels['VIT'] = 0
        
        label = f"Defender VIT {defender_debuff:+d}" if defender_debuff != 0 else "Defender VIT +0"
        ax.plot(buff_levels, damages, marker='o', label=label, linewidth=2)
    
    ax.set_xlabel('Attacker STR Buff Level', fontsize=12)
    ax.set_ylabel('Damage', fontsize=12)
    ax.set_title('Damage Progression with Increasing Buffs', fontsize=14, fontweight='bold')
    ax.set_xticks(buff_levels)
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"Progressive buff chart saved to: {output_path}")
```

- [ ] **Step 2: Test generate_progressive_buff_chart**

Run: `python3 -c "
from src.runner import load_config
from src.combat_engine import CombatEngine, Combatant
from src.visualizer import generate_progressive_buff_chart

config = load_config('config.json')

engine = CombatEngine(
    weakness_mult=config['formulas']['weakness_multiplier'],
    crit_mult=config['formulas']['crit_multiplier'],
    skill_power=config['formulas']['skill_power']
)

attacker = Combatant(name=config['attacker']['name'], base_stats=config['attacker']['stats'])
defender = Combatant(name=config['defender']['name'], base_stats=config['defender']['stats'])

generate_progressive_buff_chart(engine, attacker, defender, 'output/buff_progression.png')
"`

Expected: PNG file created at output/buff_progression.png

- [ ] **Step 3: Commit**

```bash
git add src/visualizer.py
git commit -m "feat: add generate_progressive_buff_chart line chart

Line chart showing damage scaling as attacker STR buff increases
from -3 to +3. Multiple lines for defender VIT debuff levels.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Visualizer - Buff/Debuff Matrix Heatmap

**Files:**
- Modify: `src/visualizer.py`

- [ ] **Step 1: Implement generate_buff_debuff_matrix**

Add to `src/visualizer.py`:

```python
def generate_buff_debuff_matrix(
    engine: CombatEngine,
    attacker: Combatant,
    defender: Combatant,
    output_path: str
) -> None:
    """
    Generate heatmap matrix of attacker buff vs defender debuff.
    
    Args:
        engine: CombatEngine instance
        attacker: Attacker combatant (at base buffs)
        defender: Defender combatant (at base buffs)
        output_path: Path to save PNG file
    """
    buff_levels = list(range(-3, 4))
    damage_matrix = []
    
    for defender_debuff in reversed(buff_levels):  # Reverse for visual clarity
        row = []
        for attacker_buff in buff_levels:
            # Set buffs
            attacker.buff_levels['STR'] = attacker_buff
            defender.buff_levels['VIT'] = defender_debuff
            
            # Calculate expected damage
            damage = engine.calculate_expected_damage(attacker, defender, is_weakness=False)
            row.append(damage)
        
        damage_matrix.append(row)
    
    # Reset buffs
    attacker.buff_levels['STR'] = 0
    defender.buff_levels['VIT'] = 0
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    im = ax.imshow(damage_matrix, cmap='YlOrRd', aspect='auto')
    
    # Set ticks
    ax.set_xticks(np.arange(len(buff_levels)))
    ax.set_yticks(np.arange(len(buff_levels)))
    ax.set_xticklabels([f"{b:+d}" for b in buff_levels])
    ax.set_yticklabels([f"{b:+d}" for b in reversed(buff_levels)])
    
    # Labels
    ax.set_xlabel('Attacker STR Buff Level', fontsize=12)
    ax.set_ylabel('Defender VIT Buff Level', fontsize=12)
    ax.set_title('Expected Damage Matrix (Buff × Debuff)', fontsize=14, fontweight='bold')
    
    # Add damage values as text annotations
    for i in range(len(buff_levels)):
        for j in range(len(buff_levels)):
            text = ax.text(j, i, f"{damage_matrix[i][j]:.0f}",
                          ha="center", va="center", color="black", fontsize=9)
    
    # Color bar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Damage', fontsize=12)
    
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"Buff/debuff matrix heatmap saved to: {output_path}")
```

- [ ] **Step 2: Test generate_buff_debuff_matrix**

Run: `python3 -c "
from src.runner import load_config
from src.combat_engine import CombatEngine, Combatant
from src.visualizer import generate_buff_debuff_matrix

config = load_config('config.json')

engine = CombatEngine(
    weakness_mult=config['formulas']['weakness_multiplier'],
    crit_mult=config['formulas']['crit_multiplier'],
    skill_power=config['formulas']['skill_power']
)

attacker = Combatant(name=config['attacker']['name'], base_stats=config['attacker']['stats'])
defender = Combatant(name=config['defender']['name'], base_stats=config['defender']['stats'])

generate_buff_debuff_matrix(engine, attacker, defender, 'output/buff_debuff_matrix.png')
"`

Expected: PNG file created at output/buff_debuff_matrix.png

- [ ] **Step 3: Commit**

```bash
git add src/visualizer.py
git commit -m "feat: add generate_buff_debuff_matrix heatmap

Heatmap showing expected damage for all combinations of attacker
STR buff (-3 to +3) and defender VIT debuff (-3 to +3).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Implement generate_all_graphs wrapper**

Add to `src/visualizer.py`:

```python
def generate_all_graphs(
    results: List[Dict[str, Any]],
    engine: CombatEngine,
    attacker: Combatant,
    defender: Combatant,
    output_dir: str = 'output/'
) -> None:
    """
    Generate all graph types and save to output directory.
    
    Args:
        results: List of scenario results
        engine: CombatEngine instance
        attacker: Attacker combatant
        defender: Defender combatant
        output_dir: Directory to save graphs
    """
    generate_scenario_comparison(results, os.path.join(output_dir, 'scenario_comparison.png'))
    generate_progressive_buff_chart(engine, attacker, defender, os.path.join(output_dir, 'buff_progression.png'))
    generate_buff_debuff_matrix(engine, attacker, defender, os.path.join(output_dir, 'buff_debuff_matrix.png'))
    
    print(f"\nAll graphs generated in {output_dir}")
```

- [ ] **Step 5: Commit**

```bash
git add src/visualizer.py
git commit -m "feat: add generate_all_graphs wrapper function

Generates all three graph types (bar chart, line chart, heatmap)
in one call. Saves to specified output directory.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Runner - Main Entry Point

**Files:**
- Modify: `src/runner.py`

- [ ] **Step 1: Implement main function**

Add to `src/runner.py`:

```python
import sys


def main():
    """Main entry point for SMTV combat simulator."""
    # Parse command line args
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    
    print("Loading configuration...")
    config = load_config(config_path)
    
    print("Running combat scenarios...")
    results = run_all_scenarios(config)
    
    # Print table
    print_table(results, config['attacker']['name'], config['defender']['name'])
    
    # Export CSV
    csv_path = 'output/results.csv'
    export_csv(results, csv_path)
    
    # Generate graphs
    from src.visualizer import generate_all_graphs
    
    engine = CombatEngine(
        weakness_mult=config['formulas']['weakness_multiplier'],
        crit_mult=config['formulas']['crit_multiplier'],
        skill_power=config['formulas']['skill_power']
    )
    
    attacker = Combatant(
        name=config['attacker']['name'],
        base_stats=config['attacker']['stats']
    )
    defender = Combatant(
        name=config['defender']['name'],
        base_stats=config['defender']['stats']
    )
    
    generate_all_graphs(results, engine, attacker, defender, output_dir='output/')
    
    print("\n" + "=" * 80)
    print("Simulation complete!")
    print("=" * 80)
    print(f"CSV: {csv_path}")
    print("Graphs: output/scenario_comparison.png")
    print("        output/buff_progression.png")
    print("        output/buff_debuff_matrix.png")


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Test main function**

Run: `python3 src/runner.py`

Expected:
- Table printed to terminal
- CSV created at output/results.csv
- Three PNG graphs created in output/

- [ ] **Step 3: Test with custom config**

Run: `python3 src/runner.py config.json`

Expected: Same results as step 2

- [ ] **Step 4: Commit**

```bash
git add src/runner.py
git commit -m "feat: add main entry point for CLI execution

Main function loads config, runs scenarios, prints table,
exports CSV, and generates all graphs. Accepts optional
config path argument.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 15: Documentation

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

Create `README.md`:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README

Usage instructions, configuration guide, example output,
and project structure documentation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 16: Final Integration Test

**Files:**
- None (testing existing code)

- [ ] **Step 1: Run full integration test**

Run: `python3 src/runner.py config.json`

Expected:
- No errors
- Table printed to terminal
- CSV created at output/results.csv
- Three PNG graphs created in output/

- [ ] **Step 2: Run all unit tests**

Run: `pytest tests/ -v`

Expected: All tests PASS

- [ ] **Step 3: Verify output files exist**

Run: `ls -lh output/`

Expected:
- results.csv
- scenario_comparison.png
- buff_progression.png
- buff_debuff_matrix.png

- [ ] **Step 4: Check CSV content**

Run: `head -n 10 output/results.csv`

Expected: Header row + data rows with correct columns

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "test: verify full integration

All unit tests passing. Integration test confirms:
- Config loading
- Scenario execution
- Table output
- CSV export
- Graph generation

Simulator ready for use.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Completion Checklist

After all tasks complete, verify:

- [ ] All unit tests pass (`pytest tests/ -v`)
- [ ] Integration test runs without errors (`python3 src/runner.py`)
- [ ] Output directory contains 4 files (CSV + 3 PNGs)
- [ ] README documents all features and usage
- [ ] Config file is user-editable and well-documented
- [ ] Git history shows incremental commits following TDD

## Next Steps

After implementation:

1. **Provide real SMTV stats** from your playthrough to validate formulas
2. **Research SMTV damage formulas** if needed (buff multipliers, crit rate)
3. **Create additional config files** for different scenarios (early game, late game, superboss)
4. **Experiment with extrapolation** beyond +3 buffs to test formula consistency

---

**END OF PLAN**
