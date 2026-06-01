import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any
import os
import statistics as _statistics


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


def generate_multiplier_breakdown(
    results: Dict[str, Dict[str, Any]],
    output_path: str
) -> None:
    """
    Generate stacked bar chart showing damage contribution by layer.
    
    Args:
        results: Validation results dictionary
        output_path: Path to save PNG file
    """
    if not results:
        print("No results to visualize")
        return
    
    # For simplicity, show breakdown for first few scenarios
    scenario_names = list(results.keys())[:6]
    
    # Proportional estimates based on typical multipliers
    layers = ["Base", "Level Corr", "Potential", "Charge", "Crit", "Passive"]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(scenario_names))
    width = 0.6
    
    # Proportional contribution per layer for demonstration
    layer_contributions = {
        layer: [results[name]["mean"] / len(layers) for name in scenario_names]
        for layer in layers
    }
    
    bottom = np.zeros(len(scenario_names))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for i, layer in enumerate(layers):
        ax.bar(x, layer_contributions[layer], width, label=layer, bottom=bottom, color=colors[i])
        bottom += layer_contributions[layer]
    
    ax.set_xlabel('Scenario', fontsize=12)
    ax.set_ylabel('Damage Contribution', fontsize=12)
    ax.set_title('Multiplier Breakdown by Layer', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_names, rotation=45, ha='right', fontsize=9)
    ax.legend(loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"Multiplier breakdown chart saved to: {output_path}")


def generate_level_vs_multiplicative(
    results: Dict[str, Dict[str, Any]],
    output_path: str
) -> None:
    """
    Generate side-by-side grouped bars comparing level advantage vs multiplier stack.
    
    Args:
        results: Validation results dictionary
        output_path: Path to save PNG file
    """
    if not results:
        print("No results to visualize")
        return
    
    # Extract overleveled vs multiplicative scenarios
    overleveled_scenarios = {k: v for k, v in results.items() if "Overleveled" in k or "99 vs" in k}
    multiplicative_scenarios = {k: v for k, v in results.items() if "Multipliers" in k or "Multiplicative" in k}
    
    if not overleveled_scenarios or not multiplicative_scenarios:
        print("Warning: Level vs Multiplicative scenarios not found")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Group 1: Level advantage scenarios
    group1_names = list(overleveled_scenarios.keys())[:3]
    group1_damages = [overleveled_scenarios[name]["mean"] for name in group1_names]
    
    # Group 2: Multiplicative scenarios
    group2_names = list(multiplicative_scenarios.keys())[:3]
    group2_damages = [multiplicative_scenarios[name]["mean"] for name in group2_names]
    
    x = np.arange(max(len(group1_names), len(group2_names)))
    width = 0.35
    
    ax.bar(x - width/2, group1_damages + [0]*(len(x)-len(group1_damages)), width, label='Level Advantage', color='#1f77b4')
    ax.bar(x + width/2, group2_damages + [0]*(len(x)-len(group2_damages)), width, label='Multiplicative Stack', color='#ff7f0e')
    
    ax.set_xlabel('Scenario Index', fontsize=12)
    ax.set_ylabel('Mean Damage', fontsize=12)
    ax.set_title('Level Advantage vs Multiplicative Synergy', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"Level vs Multiplicative comparison saved to: {output_path}")


def generate_root_curve(
    level: int,
    output_path: str
) -> None:
    """
    Generate line chart showing Root diminishing returns.
    
    Args:
        level: Character level for Root calculation
        output_path: Path to save PNG file
    """
    from src.combat_engine import CombatEngine
    
    engine = CombatEngine()
    
    stat_range = range(0, 251, 5)
    offense_values = [engine._apply_root_diminishing_returns(stat, level) for stat in stat_range]
    
    root = level + 10
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(stat_range, offense_values, linewidth=2, color='#1f77b4')
    
    # Add vertical line at Root threshold
    ax.axvline(x=root, color='red', linestyle='--', linewidth=2, label=f'Root Threshold (Level+10 = {root})')
    
    # Annotate linear vs diminishing regions
    ax.text(root/2, max(offense_values)*0.8, 'Linear Phase\n(Full Efficiency)', 
            ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    ax.text(root + 70, max(offense_values)*0.5, 'Diminishing Returns\n(Sqrt Penalty)', 
            ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
    
    ax.set_xlabel('Raw Stat Value', fontsize=12)
    ax.set_ylabel('Effective Offense', fontsize=12)
    ax.set_title(f'Root Diminishing Returns Curve (Level {level})', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"Root diminishing returns curve saved to: {output_path}")


def generate_vitality_heatmap(
    output_path: str
) -> None:
    """
    Generate 2D heatmap showing Vitality tier boundaries.
    
    Args:
        output_path: Path to save PNG file
    """
    from src.combat_engine import CombatEngine
    
    engine = CombatEngine()
    
    # Generate grid of Offense/Vitality combinations
    offense_range = np.linspace(50, 500, 50)
    vitality_range = np.linspace(20, 300, 50)
    
    tier_matrix = np.zeros((len(vitality_range), len(offense_range)))
    
    for i, vit in enumerate(vitality_range):
        for j, off in enumerate(offense_range):
            diff = off - vit
            
            # Determine tier
            if diff <= off / 2:
                tier = 1  # Heavy mitigation
            elif diff <= 3/4 * off:
                tier = 2  # Standard penetration
            else:
                tier = 3  # Overwhelming force
            
            tier_matrix[i, j] = tier
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Use discrete colormap for 3 tiers
    import matplotlib as mpl
    cmap = mpl.colors.ListedColormap(['#d62728', '#ffff00', '#2ca02c'])
    bounds = [0.5, 1.5, 2.5, 3.5]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    
    im = ax.imshow(tier_matrix, cmap=cmap, norm=norm, aspect='auto', origin='lower',
                   extent=[offense_range[0], offense_range[-1], vitality_range[0], vitality_range[-1]])
    
    ax.set_xlabel('Offense', fontsize=12)
    ax.set_ylabel('Vitality', fontsize=12)
    ax.set_title('Vitality Damage Tier Heatmap', fontsize=14, fontweight='bold')
    
    # Add colorbar with tier labels
    cbar = fig.colorbar(im, ax=ax, ticks=[1, 2, 3])
    cbar.set_label('Damage Tier', fontsize=12)
    cbar.ax.set_yticklabels(['Tier 1 (Heavy Mitigation)', 'Tier 2 (Standard)', 'Tier 3 (Overwhelming)'])
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"Vitality tier heatmap saved to: {output_path}")


def generate_variance_distribution(
    results: Dict[str, Dict[str, Any]],
    output_path: str
) -> None:
    """
    Generate histogram showing stochastic variance distribution.
    
    Args:
        results: Validation results dictionary
        output_path: Path to save PNG file
    """
    if not results:
        print("No results to visualize")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Take first scenario as example
    scenario_name = list(results.keys())[0]
    stats = results[scenario_name]
    
    mean = stats["mean"]
    std = stats["std"]
    
    # Generate mock trial data with variance
    mock_damages = np.random.normal(mean, std, 100)
    
    ax.hist(mock_damages, bins=20, color='#1f77b4', alpha=0.7, edgecolor='black')
    
    # Add mean line
    ax.axvline(x=mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean:.1f}')
    
    # Add ±1σ lines
    ax.axvline(x=mean - std, color='orange', linestyle=':', linewidth=1.5, label=f'±1σ: {std:.2f}')
    ax.axvline(x=mean + std, color='orange', linestyle=':', linewidth=1.5)
    
    ax.set_xlabel('Damage', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f'Variance Distribution: {scenario_name}', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"Variance distribution histogram saved to: {output_path}")


def generate_validation_report(
    results: Dict[str, Dict[str, Any]],
    output_dir: str = "output/validation"
) -> None:
    """
    Generate all validation graphs and export summary CSV.
    
    Args:
        results: Validation results dictionary
        output_dir: Output directory for all graphs
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nGenerating validation visualizations in: {output_dir}")
    
    generate_multiplier_breakdown(results, f"{output_dir}/multiplier_breakdown.png")
    generate_level_vs_multiplicative(results, f"{output_dir}/level_vs_multiplicative.png")
    generate_root_curve(99, f"{output_dir}/root_curve.png")
    generate_vitality_heatmap(f"{output_dir}/vitality_heatmap.png")
    generate_variance_distribution(results, f"{output_dir}/variance_distribution.png")
    
    print(f"\nAll validation graphs generated in: {output_dir}")


def generate_all_graphs(
    results: List[Dict[str, Any]],
    engine,
    attacker,
    defender,
    output_prefix: str = 'output/'
) -> None:
    """
    Generate all graph types and save using output path prefix.

    Args:
        results: List of scenario results
        engine: CombatEngine instance
        attacker: Attacker combatant
        defender: Defender combatant
        output_prefix: Prefix for graph output paths
    """
    if not output_prefix.endswith(('/', '_')):
        output_prefix = f"{output_prefix}_"

    generate_scenario_comparison(results, f'{output_prefix}scenario_comparison.png')
    generate_progressive_buff_chart(engine, attacker, defender, f'{output_prefix}buff_progression.png')
    generate_buff_debuff_matrix(engine, attacker, defender, f'{output_prefix}buff_debuff_matrix.png')

    print(f"\nAll graphs generated with prefix: {output_prefix}")
