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
