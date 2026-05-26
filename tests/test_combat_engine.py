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
