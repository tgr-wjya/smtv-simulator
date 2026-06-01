from dataclasses import dataclass, field
from typing import Dict, Optional, List


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
