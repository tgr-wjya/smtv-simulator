import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any
import os


def generate_scenario_comparison(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generate bar chart comparing damage across scenarios.

    Args:
        results: List of scenario results
        output_path: Path to save PNG file
    """
    if not results:
        print("No results to visualize")
        return

    scenario_names = [r['scenario_name'] for r in results]
    normal_damages = [r['damages']['normal'] for r in results]
    weakness_damages = [r['damages']['normal_weakness'] for r in results]
    crit_damages = [r['damages']['crit'] for r in results]
    crit_weakness_damages = [r['damages']['crit_weakness'] for r in results]
    percent_changes = [r['percent_change'] for r in results]

    x = np.arange(len(scenario_names))
    width = 0.2

    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot grouped bars
    rects1 = ax.bar(x - 1.5*width, normal_damages, width, label='Normal')
    rects2 = ax.bar(x - 0.5*width, weakness_damages, width, label='Weakness')
    rects3 = ax.bar(x + 0.5*width, crit_damages, width, label='Crit')
    rects4 = ax.bar(x + 1.5*width, crit_weakness_damages, width, label='Crit + Weakness')

    # Add percent change labels above normal damage bars
    for i, (rect, pct) in enumerate(zip(rects1, percent_changes)):
        height = rect.get_height()
        label = f"+{pct:.1f}%" if pct >= 0 else f"{pct:.1f}%"
        ax.text(rect.get_x() + rect.get_width()/2., height,
                label, ha='center', va='bottom', fontsize=8, rotation=45)

    ax.set_xlabel('Scenario', fontsize=12)
    ax.set_ylabel('Damage', fontsize=12)
    ax.set_title('Damage Comparison Across Scenarios', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Scenario comparison chart saved to: {output_path}")


def generate_progressive_buff_chart(
    engine,
    attacker,
    defender,
    output_path: str
) -> None:
    """
    Generate line chart showing damage as attacker STR buff increases.

    Creates multiple lines for different defender VIT debuff levels (0, -1, -2, -3).
    X-axis: attacker STR buff level (-3 to +3)
    Y-axis: damage
    Resets buffs after calculation.

    Args:
        engine: CombatEngine instance
        attacker: Attacker combatant
        defender: Defender combatant
        output_path: Path to save PNG file
    """
    from copy import deepcopy

    # Save original buff levels
    original_attacker_buffs = deepcopy(attacker.buff_levels)
    original_defender_buffs = deepcopy(defender.buff_levels)

    # STR buff range for attacker
    str_buff_range = [-3, -2, -1, 0, 1, 2, 3]

    # VIT debuff levels for defender (negative = debuff)
    vit_debuff_levels = [0, -1, -2, -3]

    # Store damage data for each VIT debuff level
    damage_data = {vit_debuff: [] for vit_debuff in vit_debuff_levels}

    # Calculate damages for each combination
    for vit_debuff in vit_debuff_levels:
        for str_buff in str_buff_range:
            # Apply buffs
            attacker.buff_levels['STR'] = str_buff
            defender.buff_levels['VIT'] = vit_debuff

            # Calculate damage (normal hit, no weakness/crit)
            damage = engine.calculate_damage(attacker, defender, is_weakness=False, is_crit=False)
            damage_data[vit_debuff].append(damage)

    # Reset buffs
    attacker.buff_levels = original_attacker_buffs
    defender.buff_levels = original_defender_buffs

    # Create line chart
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot lines for each VIT debuff level
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    for i, vit_debuff in enumerate(vit_debuff_levels):
        label = f"Defender VIT {vit_debuff:+d}" if vit_debuff != 0 else "Defender VIT 0 (baseline)"
        ax.plot(
            str_buff_range,
            damage_data[vit_debuff],
            marker='o',
            linewidth=2,
            markersize=6,
            label=label,
            color=colors[i]
        )

    ax.set_xlabel('Attacker STR Buff Level', fontsize=12)
    ax.set_ylabel('Damage', fontsize=12)
    ax.set_title('Progressive Attacker STR Buff Effect on Damage', fontsize=14, fontweight='bold')
    ax.set_xticks(str_buff_range)
    ax.set_xticklabels([f"{x:+d}" for x in str_buff_range])
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Progressive buff chart saved to: {output_path}")


def generate_buff_debuff_matrix(
    engine,
    attacker,
    defender,
    output_path: str
) -> None:
    """
    Generate heatmap matrix of attacker buff vs defender debuff.

    Args:
        engine: CombatEngine instance
        attacker: Attacker combatant (at base buffs)
        defender: Defender combatant (at base buffs)
        output_path: Path to save PNG file
    """
    from copy import deepcopy

    # Save original buff levels
    original_attacker_buffs = deepcopy(attacker.buff_levels)
    original_defender_buffs = deepcopy(defender.buff_levels)

    buff_levels = list(range(-3, 4))
    damage_matrix = []

    for defender_debuff in reversed(buff_levels):  # Reverse for visual clarity
        row = []
        for attacker_buff in buff_levels:
            # Set buffs
            attacker.buff_levels['STR'] = attacker_buff
            defender.buff_levels['VIT'] = defender_debuff

            # Calculate expected damage
            damage = engine.calculate_expected_damage(attacker, defender, is_weakness=False)
            row.append(damage)

        damage_matrix.append(row)

    # Reset buffs
    attacker.buff_levels = original_attacker_buffs
    defender.buff_levels = original_defender_buffs

    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(damage_matrix, cmap='YlOrRd', aspect='auto')

    # Set ticks
    ax.set_xticks(np.arange(len(buff_levels)))
    ax.set_yticks(np.arange(len(buff_levels)))
    ax.set_xticklabels([f"{b:+d}" for b in buff_levels])
    ax.set_yticklabels([f"{b:+d}" for b in reversed(buff_levels)])

    # Labels
    ax.set_xlabel('Attacker STR Buff Level', fontsize=12)
    ax.set_ylabel('Defender VIT Buff Level', fontsize=12)
    ax.set_title('Expected Damage Matrix (Buff × Debuff)', fontsize=14, fontweight='bold')

    # Add damage values as text annotations
    for i in range(len(buff_levels)):
        for j in range(len(buff_levels)):
            text = ax.text(j, i, f"{damage_matrix[i][j]:.0f}",
                          ha="center", va="center", color="black", fontsize=9)

    # Color bar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Damage', fontsize=12)

    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Buff/debuff matrix heatmap saved to: {output_path}")


def generate_all_graphs(
    results: List[Dict[str, Any]],
    engine,
    attacker,
    defender,
    output_dir: str = 'output/'
) -> None:
    """
    Generate all graph types and save to output directory.

    Args:
        results: List of scenario results
        engine: CombatEngine instance
        attacker: Attacker combatant
        defender: Defender combatant
        output_dir: Directory to save graphs
    """
    generate_scenario_comparison(results, os.path.join(output_dir, 'scenario_comparison.png'))
    generate_progressive_buff_chart(engine, attacker, defender, os.path.join(output_dir, 'buff_progression.png'))
    generate_buff_debuff_matrix(engine, attacker, defender, os.path.join(output_dir, 'buff_debuff_matrix.png'))

    print(f"\nAll graphs generated in {output_dir}")
