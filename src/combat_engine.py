import math
import random
from dataclasses import dataclass, field
from typing import Dict, Optional, List


# Vengeance Mechanics Constants

# Skill Potential → multiplier (DEBUNKED §8)
POTENTIAL_MULTIPLIERS = {
    -9: 0.45,
    -4: 0.75,
    0: 1.0,
    4: 1.25,
    5: 1.35,
    9: 1.55
}

# Charge state multipliers (DEBUNKED §8)
CHARGE_MULTIPLIERS = {
    "charge": 1.8,
    "concentrate": 1.8,
    "donum_gladi": 1.5,
    "donum_magici": 1.5,
    "impaler_animus": 1.3,
    "impaler_glory": 3.4,
}

# Elemental resistance (DEBUNKED §9)
RESISTANCE_MULTIPLIERS = {
    "immune": 0.0,
    "drain": -1.0,
    "repel": -0.5,
    "resist": 0.5,
    "neutral": 1.0,
    "weak": 1.5,
}

# Critical Zealot passive (DEBUNKED §9)
CRIT_ZEALOT_NON_CRIT = 0.9
CRIT_ZEALOT_CRIT = 1.45

# Guard multiplier (DEBUNKED §6)
GUARD_MULTIPLIER = 0.8


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
    level: int
    buff_levels: Dict[str, int] = field(default_factory=lambda: {
        'STR': 0, 'VIT': 0, 'MAG': 0, 'AGI': 0, 'LUC': 0
    })

    # New Vengeance fields
    skill_potentials: Dict[str, int] = field(default_factory=dict)
    charge_state: Optional[str] = None
    passive_abilities: List[str] = field(default_factory=list)
    guarding: bool = False
    doubler_active: bool = False

    def get_effective_stat(self, stat: str) -> float:
        """Calculate effective stat value with buff multiplier applied"""
        base_value = self.base_stats[stat]
        buff_level = self.buff_levels[stat]
        multiplier = BUFF_MULTIPLIERS[buff_level]
        return base_value * multiplier

    def apply_buff(self, stat: str, delta: int) -> None:
        """
        Apply buff/debuff to a stat. Clamped to [-3, +3].

        Args:
            stat: Stat name ('STR', 'VIT', etc.)
            delta: Change amount (positive = buff, negative = debuff)
        """
        new_level = self.buff_levels[stat] + delta
        self.buff_levels[stat] = max(-3, min(3, new_level))

    def apply_all_buffs(self, delta: int) -> None:
        """
        Apply same buff/debuff to all stats.

        Args:
            delta: Change amount (positive = buff, negative = debuff)
        """
        for stat in self.buff_levels.keys():
            self.apply_buff(stat, delta)


class CombatEngine:
    """Handles damage calculation with SMTV formulas"""

    # Passive ability registry (extensible for GUI)
    PASSIVE_EFFECTS = {
        "critical_zealot": lambda state: {
            "damage_mult": CRIT_ZEALOT_CRIT if state.get("is_crit", False) else CRIT_ZEALOT_NON_CRIT
        },
        "murderous_glee": lambda state: {
            "crit_rate_mult": 2.5
        },
    }

    def __init__(
        self,
        weakness_mult: float = 1.5,
        crit_mult: float = 1.5,
        skill_power: int = 100
    ):
        self.weakness_multiplier = weakness_mult
        self.crit_multiplier = crit_mult
        self.skill_power = skill_power

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

    def calculate_crit_rate(
        self,
        attacker: Combatant,
        defender: Combatant
    ) -> float:
        """
        Calculate critical hit rate.

        Formula: 5% base + (effective_LUC_diff × 0.2%), capped [0%, 100%]

        Args:
            attacker: Attacking combatant
            defender: Defending combatant

        Returns:
            Critical hit rate as decimal (0.0 to 1.0)
        """
        effective_attacker_luc = attacker.get_effective_stat('LUC')
        effective_defender_luc = defender.get_effective_stat('LUC')

        luc_diff = effective_attacker_luc - effective_defender_luc
        crit_rate = 0.05 + (luc_diff * 0.002)

        # Cap at [0%, 100%]
        crit_rate = max(0.0, min(1.0, crit_rate))
        return crit_rate

    def calculate_damage(
        self,
        attacker: Combatant,
        defender: Combatant,
        is_weakness: bool,
        is_crit: bool
    ) -> float:
        """
        Calculate damage with weakness and crit multipliers.

        Formula: base_damage × weakness_mult × crit_mult

        Args:
            attacker: Attacking combatant
            defender: Defending combatant
            is_weakness: Whether hit exploits weakness
            is_crit: Whether hit is critical

        Returns:
            Calculated damage
        """
        base_damage = self.calculate_base_damage(attacker, defender)

        weakness_mult = self.weakness_multiplier if is_weakness else 1.0
        crit_mult = self.crit_multiplier if is_crit else 1.0

        damage = base_damage * weakness_mult * crit_mult
        return damage

    def calculate_expected_damage(
        self,
        attacker: Combatant,
        defender: Combatant,
        is_weakness: bool
    ) -> float:
        """
        Calculate expected damage weighted by crit rate.

        Formula: normal_dmg × (1 - crit_rate) + crit_dmg × crit_rate

        Args:
            attacker: Attacking combatant
            defender: Defending combatant
            is_weakness: Whether hit exploits weakness

        Returns:
            Expected damage value
        """
        crit_rate = self.calculate_crit_rate(attacker, defender)

        normal_damage = self.calculate_damage(attacker, defender, is_weakness=is_weakness, is_crit=False)
        crit_damage = self.calculate_damage(attacker, defender, is_weakness=is_weakness, is_crit=True)

        expected_damage = normal_damage * (1 - crit_rate) + crit_damage * crit_rate
        return expected_damage

    def _apply_root_diminishing_returns(self, stat: int, level: int) -> float:
        """
        Convert raw stat to Offense using Root formula (DEBUNKED §3).

        Root = Level + 10
        If stat <= Root: Offense = stat * 2 (linear, full efficiency)
        If stat > Root: Offense = Root + sqrt(stat - Root) + Root (diminishing returns)
        """
        root = level + 10
        if stat <= root:
            return stat * 2.0
        else:
            return root + math.sqrt(stat - root) + root

    def _calculate_level_correction(self, attacker_level: int, defender_level: int) -> float:
        """
        Calculate Level Correction multiplier with bounded 0.5x-1.5x range (DEBUNKED §5).
        """
        diff = attacker_level - defender_level
        if abs(diff) <= 2:
            return 1.0
        combined = attacker_level + defender_level
        if combined <= 30:
            sum_factor = 0.0
        elif combined <= 130:
            sum_factor = (combined - 30) / 1000
        else:
            sum_factor = 0.1
        correction = 1.0 + (diff * sum_factor)
        return max(0.5, min(1.5, correction))

    def _calculate_base_damage(self, offense: float, vitality: float) -> float:
        """
        Calculate base damage using 3-tier Vitality formula (DEBUNKED §4).
        """
        diff = offense - vitality
        if diff <= offense / 2:
            return (2/3 * offense) - (1/3 * vitality) - (1/3 * math.sqrt(vitality - offense/2))
        elif diff <= 3/4 * offense:
            return offense - vitality
        else:
            return (5/6 * offense) - (1/3 * vitality) + (1/3 * math.sqrt(offense/4 - vitality))

    def _apply_skill_potential(self, potential: int) -> float:
        """Get damage multiplier from Skill Potential (DEBUNKED §8)."""
        return POTENTIAL_MULTIPLIERS.get(potential, 1.0)

    def _apply_charge_state(self, charge_state: Optional[str]) -> float:
        """Get damage multiplier from Charge state (DEBUNKED §8)."""
        if charge_state is None:
            return 1.0
        return CHARGE_MULTIPLIERS.get(charge_state, 1.0)

    def _apply_elemental_resistance(self, resistance: str) -> float:
        """Get damage multiplier from elemental resistance (DEBUNKED §9)."""
        return RESISTANCE_MULTIPLIERS.get(resistance, 1.0)

    def _apply_passives(self, passive_abilities: List[str], damage_state: dict) -> dict:
        """
        Apply passive ability effects to damage state (DEBUNKED §9).
        """
        for ability_id in passive_abilities:
            if ability_id in self.PASSIVE_EFFECTS:
                modifiers = self.PASSIVE_EFFECTS[ability_id](damage_state)
                damage_state.update(modifiers)
        return damage_state

    def _apply_variance(self, base_damage: float) -> float:
        """
        Apply stochastic variance (DEBUNKED §12).
        """
        if base_damage < 10:
            return base_damage
        var1 = random.randint(0, int(0.1 * base_damage))
        var2 = random.randint(0, 4)
        return base_damage + var1 + var2

    def _apply_guard(self, guarding: bool) -> float:
        """Apply Guard damage reduction (DEBUNKED §6)."""
        if guarding:
            return GUARD_MULTIPLIER
        return 1.0

    def _apply_doubler_bug(self, doubler_active: bool, defense_debuff: int) -> float:
        """
        Apply Doubler bug mechanic (DEBUNKED §13).
        Bug: mistakenly queries Attack instead of Defense. With -2 debuff -> 0.01x.
        """
        if doubler_active and defense_debuff < 0:
            return 0.01
        return 1.0

    def calculate_vengeance_damage(
        self,
        attacker: 'Combatant',
        defender: 'Combatant',
        skill_element: str,
        resistance: str,
        is_crit: bool
    ) -> float:
        """
        Calculate damage using complete Vengeance mechanics pipeline (9 layers).

        Layer order:
        1. Stat Scaling (Root diminishing returns)
        2. Level Correction (bounded 0.5x-1.5x)
        3. Base Damage (3-tier Vitality)
        4. Skill Modifiers (Potential + Charge)
        5. Crit Calculation
        6. Resistance
        7. Passive Abilities
        8. Stochastic Variance
        9. Defense (Guard, Doubler)
        """
        # Layer 1: Stat Scaling
        effective_str = attacker.get_effective_stat('STR')
        raw_offense = self._apply_root_diminishing_returns(int(effective_str), attacker.level)

        # Layer 2: Level Correction
        level_correction = self._calculate_level_correction(attacker.level, defender.level)
        offense = raw_offense * level_correction

        # Layer 3: Base Damage (3-tier Vitality)
        effective_vit = defender.get_effective_stat('VIT')
        base_damage = self._calculate_base_damage(offense, effective_vit)

        # Layer 4: Skill Modifiers
        potential = attacker.skill_potentials.get(skill_element, 0)
        potential_mult = self._apply_skill_potential(potential)
        charge_mult = self._apply_charge_state(attacker.charge_state)
        damage = base_damage * potential_mult * charge_mult

        # Layer 5: Crit
        if is_crit:
            damage *= self.crit_multiplier

        # Layer 6: Resistance
        resistance_mult = self._apply_elemental_resistance(resistance)
        damage *= resistance_mult

        # Layer 7: Passive Abilities
        damage_state = {"is_crit": is_crit, "base_damage": damage}
        damage_state = self._apply_passives(attacker.passive_abilities, damage_state)
        if "damage_mult" in damage_state:
            damage *= damage_state["damage_mult"]

        # Layer 8: Stochastic Variance
        damage = self._apply_variance(damage)

        # Layer 9: Defense
        guard_mult = self._apply_guard(defender.guarding)
        damage *= guard_mult
        doubler_mult = self._apply_doubler_bug(
            defender.doubler_active,
            defender.buff_levels.get('VIT', 0)
        )
        damage *= doubler_mult

        return damage
