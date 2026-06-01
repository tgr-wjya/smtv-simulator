import pytest
import random
from src.combat_engine import (
    Combatant,
    CombatEngine,
    POTENTIAL_MULTIPLIERS,
    CHARGE_MULTIPLIERS,
    RESISTANCE_MULTIPLIERS,
    CRIT_ZEALOT_NON_CRIT,
    CRIT_ZEALOT_CRIT,
    GUARD_MULTIPLIER
)


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


# --- Constants Tests ---

def test_potential_multipliers():
    assert POTENTIAL_MULTIPLIERS[-9] == 0.45
    assert POTENTIAL_MULTIPLIERS[-4] == 0.75
    assert POTENTIAL_MULTIPLIERS[0] == 1.0
    assert POTENTIAL_MULTIPLIERS[4] == 1.25
    assert POTENTIAL_MULTIPLIERS[5] == 1.35
    assert POTENTIAL_MULTIPLIERS[9] == 1.55


def test_charge_multipliers():
    assert CHARGE_MULTIPLIERS["charge"] == 1.8
    assert CHARGE_MULTIPLIERS["concentrate"] == 1.8
    assert CHARGE_MULTIPLIERS["donum_gladi"] == 1.5
    assert CHARGE_MULTIPLIERS["donum_magici"] == 1.5
    assert CHARGE_MULTIPLIERS["impaler_animus"] == 1.3
    assert CHARGE_MULTIPLIERS["impaler_glory"] == 3.4


def test_resistance_multipliers():
    assert RESISTANCE_MULTIPLIERS["immune"] == 0.0
    assert RESISTANCE_MULTIPLIERS["drain"] == -1.0
    assert RESISTANCE_MULTIPLIERS["repel"] == -0.5
    assert RESISTANCE_MULTIPLIERS["resist"] == 0.5
    assert RESISTANCE_MULTIPLIERS["neutral"] == 1.0
    assert RESISTANCE_MULTIPLIERS["weak"] == 1.5


def test_crit_zealot_constants():
    assert CRIT_ZEALOT_NON_CRIT == 0.9
    assert CRIT_ZEALOT_CRIT == 1.45


def test_guard_multiplier():
    assert GUARD_MULTIPLIER == 0.8


# --- Root Diminishing Returns ---

def test_root_diminishing_returns_linear_phase():
    engine = CombatEngine()
    assert engine._apply_root_diminishing_returns(109, 99) == 218.0
    assert engine._apply_root_diminishing_returns(100, 99) == 200.0


def test_root_diminishing_returns_penalty_phase():
    engine = CombatEngine()
    assert abs(engine._apply_root_diminishing_returns(120, 99) - 221.317) < 0.01
    assert abs(engine._apply_root_diminishing_returns(160, 99) - 225.141) < 0.01
    assert abs(engine._apply_root_diminishing_returns(250, 99) - 229.874) < 0.01


def test_root_threshold_scales_with_level():
    engine = CombatEngine()
    assert engine._apply_root_diminishing_returns(60, 50) == 120.0
    assert engine._apply_root_diminishing_returns(20, 10) == 40.0


# --- Level Correction ---

def test_level_correction_near_peer():
    engine = CombatEngine()
    assert engine._calculate_level_correction(99, 99) == 1.0
    assert engine._calculate_level_correction(99, 97) == 1.0
    assert engine._calculate_level_correction(95, 97) == 1.0


def test_level_correction_floor():
    engine = CombatEngine()
    assert engine._calculate_level_correction(80, 99) >= 0.5
    assert engine._calculate_level_correction(50, 99) == 0.5


def test_level_correction_ceiling():
    engine = CombatEngine()
    assert engine._calculate_level_correction(99, 85) <= 1.5
    assert engine._calculate_level_correction(99, 50) == 1.5


def test_level_correction_sum_factor():
    engine = CombatEngine()
    # Early game
    assert engine._calculate_level_correction(15, 15) == 1.0
    # Late game capped to 1.5
    assert engine._calculate_level_correction(99, 85) == 1.5
    assert engine._calculate_level_correction(70, 65) == 1.5


# --- 3-Tier Vitality ---

def test_vitality_tier1_heavy_mitigation():
    engine = CombatEngine()
    base_damage = engine._calculate_base_damage(200.0, 150.0)
    assert abs(base_damage - 80.97) < 0.1


def test_vitality_tier2_standard_penetration():
    engine = CombatEngine()
    assert engine._calculate_base_damage(200.0, 80.0) == 120.0


def test_vitality_tier3_overwhelming_force():
    engine = CombatEngine()
    base_damage = engine._calculate_base_damage(200.0, 30.0)
    assert abs(base_damage - 158.16) < 0.1


def test_vitality_tier_boundaries():
    engine = CombatEngine()
    offense = 300.0
    damage_tier1 = engine._calculate_base_damage(offense, offense - (offense / 2))
    damage_tier2_low = engine._calculate_base_damage(offense, offense - (offense / 2 + 1))
    damage_tier3 = engine._calculate_base_damage(offense, offense - (3/4 * offense + 1))
    assert damage_tier1 < damage_tier2_low
    assert damage_tier3 > damage_tier2_low


# --- Skill Potential ---

def test_skill_potential_neutral():
    assert CombatEngine()._apply_skill_potential(0) == 1.0


def test_skill_potential_positive():
    engine = CombatEngine()
    assert engine._apply_skill_potential(4) == 1.25
    assert engine._apply_skill_potential(9) == 1.55


def test_skill_potential_negative():
    engine = CombatEngine()
    assert engine._apply_skill_potential(-4) == 0.75
    assert engine._apply_skill_potential(-9) == 0.45


def test_skill_potential_default_neutral():
    assert CombatEngine()._apply_skill_potential(2) == 1.0


# --- Charge States ---

def test_charge_state_none():
    assert CombatEngine()._apply_charge_state(None) == 1.0


def test_charge_state_basic():
    engine = CombatEngine()
    assert engine._apply_charge_state("charge") == 1.8
    assert engine._apply_charge_state("concentrate") == 1.8


def test_charge_state_donum():
    engine = CombatEngine()
    assert engine._apply_charge_state("donum_gladi") == 1.5
    assert engine._apply_charge_state("donum_magici") == 1.5


def test_charge_state_impaler():
    engine = CombatEngine()
    assert engine._apply_charge_state("impaler_animus") == 1.3
    assert engine._apply_charge_state("impaler_glory") == 3.4


def test_charge_state_invalid():
    assert CombatEngine()._apply_charge_state("invalid_charge") == 1.0


# --- Elemental Resistance ---

def test_resistance_neutral():
    assert CombatEngine()._apply_elemental_resistance("neutral") == 1.0

def test_resistance_weak():
    assert CombatEngine()._apply_elemental_resistance("weak") == 1.5

def test_resistance_resist():
    assert CombatEngine()._apply_elemental_resistance("resist") == 0.5

def test_resistance_repel():
    assert CombatEngine()._apply_elemental_resistance("repel") == -0.5

def test_resistance_drain():
    assert CombatEngine()._apply_elemental_resistance("drain") == -1.0

def test_resistance_immune():
    assert CombatEngine()._apply_elemental_resistance("immune") == 0.0

def test_resistance_invalid():
    assert CombatEngine()._apply_elemental_resistance("invalid") == 1.0


# --- Passive Abilities ---

def test_passive_registry_exists():
    engine = CombatEngine()
    assert hasattr(engine, 'PASSIVE_EFFECTS')
    assert "critical_zealot" in engine.PASSIVE_EFFECTS
    assert "murderous_glee" in engine.PASSIVE_EFFECTS


def test_critical_zealot_non_crit():
    engine = CombatEngine()
    result = engine._apply_passives(["critical_zealot"], {"is_crit": False, "base_damage": 100.0})
    assert result["damage_mult"] == 0.9


def test_critical_zealot_crit():
    engine = CombatEngine()
    result = engine._apply_passives(["critical_zealot"], {"is_crit": True, "base_damage": 100.0})
    assert result["damage_mult"] == 1.45


def test_murderous_glee_crit_rate():
    engine = CombatEngine()
    result = engine._apply_passives(["murderous_glee"], {"is_crit": False, "crit_rate": 0.2})
    assert result["crit_rate_mult"] == 2.5


def test_multiple_passives():
    engine = CombatEngine()
    result = engine._apply_passives(["critical_zealot", "murderous_glee"], {"is_crit": True, "crit_rate": 0.2})
    assert result["damage_mult"] == 1.45
    assert result["crit_rate_mult"] == 2.5


def test_no_passives():
    engine = CombatEngine()
    state = {"is_crit": False, "base_damage": 100.0}
    result = engine._apply_passives([], state)
    assert result == state


def test_invalid_passive():
    engine = CombatEngine()
    state = {"is_crit": False, "base_damage": 100.0}
    result = engine._apply_passives(["invalid_passive"], state)
    assert "damage_mult" not in result


# --- Stochastic Variance ---

def test_variance_below_threshold():
    engine = CombatEngine()
    assert engine._apply_variance(5.0) == 5.0
    assert engine._apply_variance(9.9) == 9.9


def test_variance_applied():
    engine = CombatEngine()
    results = [engine._apply_variance(100.0) for _ in range(100)]
    assert all(d >= 100.0 for d in results)
    assert all(d <= 114.0 for d in results)
    assert len(set(results)) > 1


def test_variance_deterministic_seed():
    engine = CombatEngine()
    random.seed(42)
    d1 = engine._apply_variance(100.0)
    random.seed(42)
    d2 = engine._apply_variance(100.0)
    assert d1 == d2


# --- Guard & Doubler ---

def test_guard_active():
    assert CombatEngine()._apply_guard(True) == 0.8

def test_guard_inactive():
    assert CombatEngine()._apply_guard(False) == 1.0

def test_doubler_bug_active():
    assert CombatEngine()._apply_doubler_bug(True, -2) == 0.01

def test_doubler_bug_inactive():
    assert CombatEngine()._apply_doubler_bug(False, -2) == 1.0


# --- Full Pipeline ---

def test_full_vengeance_pipeline():
    engine = CombatEngine(skill_power=100)
    attacker = Combatant(
        name="Nahobino",
        base_stats={'STR': 109, 'VIT': 80, 'MAG': 109, 'AGI': 70, 'LUC': 110},
        level=99,
        skill_potentials={"phys": 9},
        charge_state="impaler_glory",
        passive_abilities=["critical_zealot"]
    )
    defender = Combatant(
        name="Demi-Fiend",
        base_stats={'STR': 40, 'VIT': 80, 'MAG': 40, 'AGI': 60, 'LUC': 64},
        level=95,
        guarding=False
    )
    attacker.buff_levels['STR'] = 2
    defender.buff_levels['VIT'] = -2
    damage = engine.calculate_vengeance_damage(
        attacker=attacker,
        defender=defender,
        skill_element="phys",
        resistance="neutral",
        is_crit=True
    )
    assert damage > 0
    assert damage > 500


def test_vengeance_vs_vanilla_comparison():
    engine = CombatEngine(skill_power=100)
    attacker = Combatant(
        name="Test",
        base_stats={'STR': 109, 'VIT': 80, 'MAG': 109, 'AGI': 70, 'LUC': 110},
        level=99,
        skill_potentials={"phys": 9},
        charge_state="impaler_glory"
    )
    defender = Combatant(
        name="Test",
        base_stats={'STR': 40, 'VIT': 80, 'MAG': 40, 'AGI': 60, 'LUC': 64},
        level=95
    )
    vengeance_damage = engine.calculate_vengeance_damage(
        attacker=attacker, defender=defender,
        skill_element="phys", resistance="neutral", is_crit=False
    )
    vanilla_damage = engine.calculate_damage(
        attacker=attacker, defender=defender,
        is_weakness=False, is_crit=False
    )
    assert vengeance_damage != vanilla_damage
