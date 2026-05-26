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
