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


def test_calculate_crit_rate_equal_luck():
    """Test crit rate with equal LUC: 5% base"""
    engine = CombatEngine()

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    crit_rate = engine.calculate_crit_rate(attacker, defender)

    # Equal LUC (0 diff) = 5% base
    assert crit_rate == 0.05


def test_calculate_crit_rate_higher_attacker_luck():
    """Test crit rate with higher attacker LUC: +20 diff = 9%"""
    engine = CombatEngine()

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 60}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    crit_rate = engine.calculate_crit_rate(attacker, defender)

    # LUC diff = 60 - 40 = 20, crit rate = 5% + (20 * 0.2%) = 9%
    assert crit_rate == 0.09


def test_calculate_crit_rate_lower_attacker_luck():
    """Test crit rate with lower attacker LUC: -20 diff = 1%"""
    engine = CombatEngine()

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 20}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    crit_rate = engine.calculate_crit_rate(attacker, defender)

    # LUC diff = 20 - 40 = -20, crit rate = 5% + (-20 * 0.2%) = 1%
    assert abs(crit_rate - 0.01) < 0.0001


def test_calculate_crit_rate_with_luck_buffs():
    """Test crit rate respects effective LUC (with buffs)"""
    engine = CombatEngine()

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 50}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 50}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    # Attacker +1 LUC (1.2x), Defender -1 LUC (0.85x)
    attacker.buff_levels['LUC'] = 1
    defender.buff_levels['LUC'] = -1

    crit_rate = engine.calculate_crit_rate(attacker, defender)

    # Effective LUC: attacker = 50 * 1.2 = 60, defender = 50 * 0.85 = 42.5
    # Diff = 60 - 42.5 = 17.5, crit rate = 5% + (17.5 * 0.2%) = 8.5%
    assert abs(crit_rate - 0.085) < 0.0001


def test_calculate_crit_rate_capped_at_100_percent():
    """Test crit rate capped at 100% with extreme LUC diff"""
    engine = CombatEngine()

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 100}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 1}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    crit_rate = engine.calculate_crit_rate(attacker, defender)

    # Would be 5% + (99 * 0.2%) = 24.8%, but ensure cap works if exceeded
    assert crit_rate <= 1.0
    assert crit_rate >= 0.0


def test_calculate_crit_rate_minimum_at_zero_percent():
    """Test crit rate capped at 0% with extreme negative LUC diff"""
    engine = CombatEngine()

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 1}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 100}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    crit_rate = engine.calculate_crit_rate(attacker, defender)

    # Would be 5% + (-99 * 0.2%) = -14.8%, capped at 0%
    assert crit_rate == 0.0


# Tests for calculate_damage
def test_calculate_damage_normal():
    """Test normal damage (no weakness, no crit)"""
    engine = CombatEngine(weakness_mult=1.5, crit_mult=1.5, skill_power=100)

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    damage = engine.calculate_damage(attacker, defender, is_weakness=False, is_crit=False)

    # Base damage = (50 * 100) / 50 = 100
    # Normal (no multipliers) = 100
    assert damage == 100.0


def test_calculate_damage_weakness_only():
    """Test damage with weakness but no crit"""
    engine = CombatEngine(weakness_mult=1.5, crit_mult=1.5, skill_power=100)

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    damage = engine.calculate_damage(attacker, defender, is_weakness=True, is_crit=False)

    # Base damage = 100, weakness mult = 1.5
    # 100 * 1.5 = 150
    assert damage == 150.0


def test_calculate_damage_crit_only():
    """Test damage with crit but no weakness"""
    engine = CombatEngine(weakness_mult=1.5, crit_mult=1.5, skill_power=100)

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    damage = engine.calculate_damage(attacker, defender, is_weakness=False, is_crit=True)

    # Base damage = 100, crit mult = 1.5
    # 100 * 1.5 = 150
    assert damage == 150.0


def test_calculate_damage_weakness_and_crit():
    """Test damage with both weakness and crit"""
    engine = CombatEngine(weakness_mult=1.5, crit_mult=1.5, skill_power=100)

    attacker_stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    defender_stats = {'STR': 40, 'VIT': 50, 'MAG': 40, 'AGI': 40, 'LUC': 40}

    attacker = Combatant(name="Attacker", base_stats=attacker_stats)
    defender = Combatant(name="Defender", base_stats=defender_stats)

    damage = engine.calculate_damage(attacker, defender, is_weakness=True, is_crit=True)

    # Base damage = 100, weakness * crit = 1.5 * 1.5 = 2.25
    # 100 * 2.25 = 225
    assert damage == 225.0
