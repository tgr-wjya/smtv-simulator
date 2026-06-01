import pytest
from src.combat_engine import Combatant


def test_combatant_new_fields_defaults():
    """Test new Vengeance fields have correct defaults"""
    stats = {'STR': 50, 'VIT': 40, 'MAG': 40, 'AGI': 40, 'LUC': 40}
    combatant = Combatant(name="Test", base_stats=stats, level=99)

    assert combatant.level == 99
    assert combatant.skill_potentials == {}
    assert combatant.charge_state is None
    assert combatant.passive_abilities == []
    assert combatant.guarding is False
    assert combatant.doubler_active is False


def test_combatant_new_fields_set():
    """Test new Vengeance fields can be initialized"""
    stats = {'STR': 109, 'VIT': 80, 'MAG': 109, 'AGI': 70, 'LUC': 110}
    combatant = Combatant(
        name="Nahobino",
        base_stats=stats,
        level=99,
        skill_potentials={"phys": 9, "fire": 5},
        charge_state="impaler_glory",
        passive_abilities=["critical_zealot"],
        guarding=False
    )

    assert combatant.skill_potentials == {"phys": 9, "fire": 5}
    assert combatant.charge_state == "impaler_glory"
    assert combatant.passive_abilities == ["critical_zealot"]
