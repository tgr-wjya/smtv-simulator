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
