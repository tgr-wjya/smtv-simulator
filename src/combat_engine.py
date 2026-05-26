from dataclasses import dataclass, field
from typing import Dict


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
