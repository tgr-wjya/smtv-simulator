import os
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from src.combat_engine import CombatEngine, Combatant

# Set theme and styling
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SMTV_GUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SMTV: Vengeance Interactive Combat Simulator")
        self.geometry("1200x800")
        self.minsize(1100, 750)

        # Set up grid layout (1 row, 3 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  # Left: Nahobino
        self.grid_columnconfigure(1, weight=1)  # Middle: Target/Buffs
        self.grid_columnconfigure(2, weight=1)  # Right: Live Results

        # Initialize Combat Engine
        self.engine = CombatEngine()

        self._create_widgets()
        self.update_simulation()

    def _create_widgets(self):
        # ----------------------------------------------------
        # COLUMN 0: Nahobino (Attacker) Designer Panel
        # ----------------------------------------------------
        self.left_frame = ctk.CTkFrame(self, corner_radius=15)
        self.left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)

        left_title = ctk.CTkLabel(self.left_frame, text="Nahobino Designer (Attacker)", font=ctk.CTkFont(size=18, weight="bold"))
        left_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Level Selector
        self.level_label = ctk.CTkLabel(self.left_frame, text="Level: 99", font=ctk.CTkFont(size=13))
        self.level_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.level_slider = ctk.CTkSlider(self.left_frame, from_=1, to=99, command=self._on_level_change)
        self.level_slider.set(99)
        self.level_slider.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # STR Stat Selector
        self.str_label = ctk.CTkLabel(self.left_frame, text="STR Stat: 109", font=ctk.CTkFont(size=13))
        self.str_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.str_slider = ctk.CTkSlider(self.left_frame, from_=10, to=250, command=self._on_str_change)
        self.str_slider.set(109)
        self.str_slider.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # MAG Stat Selector
        self.mag_label = ctk.CTkLabel(self.left_frame, text="MAG Stat: 109", font=ctk.CTkFont(size=13))
        self.mag_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.mag_slider = ctk.CTkSlider(self.left_frame, from_=10, to=250, command=self._on_mag_change)
        self.mag_slider.set(109)
        self.mag_slider.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # LUC Stat Selector
        self.luc_label = ctk.CTkLabel(self.left_frame, text="LUC Stat: 110", font=ctk.CTkFont(size=13))
        self.luc_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.luc_slider = ctk.CTkSlider(self.left_frame, from_=10, to=250, command=self._on_luc_change)
        self.luc_slider.set(110)
        self.luc_slider.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Skill Affinity Element Selection
        ctk.CTkLabel(self.left_frame, text="Skill Element:", font=ctk.CTkFont(size=13)).grid(row=9, column=0, padx=20, pady=(10, 0), sticky="w")
        self.element_menu = ctk.CTkOptionMenu(
            self.left_frame,
            values=["phys", "fire", "ice", "elec", "wind", "light", "dark", "force", "magic"],
            command=self._on_dropdown_change
        )
        self.element_menu.set("phys")
        self.element_menu.grid(row=10, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Skill Power Selector
        ctk.CTkLabel(self.left_frame, text="Skill Preset Power:", font=ctk.CTkFont(size=13)).grid(row=11, column=0, padx=20, pady=(10, 0), sticky="w")
        self.power_menu = ctk.CTkOptionMenu(
            self.left_frame,
            values=["Light (30 power)", "Medium (70 power)", "Heavy (120 power)", "Severe (200 power)"],
            command=self._on_dropdown_change
        )
        self.power_menu.set("Heavy (120 power)")
        self.power_menu.grid(row=12, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Potential Selector
        self.potential_label = ctk.CTkLabel(self.left_frame, text="Skill Potential: +9", font=ctk.CTkFont(size=13))
        self.potential_label.grid(row=13, column=0, padx=20, pady=(10, 0), sticky="w")
        self.potential_slider = ctk.CTkSlider(self.left_frame, from_=-9, to=9, number_of_steps=18, command=self._on_potential_change)
        self.potential_slider.set(9)
        self.potential_slider.grid(row=14, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Charge States
        ctk.CTkLabel(self.left_frame, text="Charge Modifier:", font=ctk.CTkFont(size=13)).grid(row=15, column=0, padx=20, pady=(10, 0), sticky="w")
        self.charge_var = ctk.StringVar(value="impaler_glory")
        
        self.charge_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.charge_frame.grid(row=16, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.charge_r0 = ctk.CTkRadioButton(self.charge_frame, text="None", variable=self.charge_var, value="none", command=self._on_toggle_change)
        self.charge_r0.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.charge_r1 = ctk.CTkRadioButton(self.charge_frame, text="Charge (1.8x)", variable=self.charge_var, value="charge", command=self._on_toggle_change)
        self.charge_r1.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.charge_r2 = ctk.CTkRadioButton(self.charge_frame, text="Concentrate (1.8x)", variable=self.charge_var, value="concentrate", command=self._on_toggle_change)
        self.charge_r2.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
        self.charge_r3 = ctk.CTkRadioButton(self.charge_frame, text="Impaler's Glory (3.4x)", variable=self.charge_var, value="impaler_glory", command=self._on_toggle_change)
        self.charge_r3.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Passives
        ctk.CTkLabel(self.left_frame, text="Passive Abilities:", font=ctk.CTkFont(size=13)).grid(row=17, column=0, padx=20, pady=(10, 0), sticky="w")
        self.cz_var = ctk.BooleanVar(value=True)
        self.cz_check = ctk.CTkCheckBox(self.left_frame, text="Critical Zealot (1.45x Crit / 0.9x Non-Crit)", variable=self.cz_var, command=self._on_toggle_change)
        self.cz_check.grid(row=18, column=0, padx=20, pady=5, sticky="w")

        self.mg_var = ctk.BooleanVar(value=False)
        self.mg_check = ctk.CTkCheckBox(self.left_frame, text="Murderous Glee (2.5x Crit Rate multiplier)", variable=self.mg_var, command=self._on_toggle_change)
        self.mg_check.grid(row=19, column=0, padx=20, pady=(5, 15), sticky="w")

        # ----------------------------------------------------
        # COLUMN 1: Target (Defender) & Buffs Designer Panel
        # ----------------------------------------------------
        self.mid_frame = ctk.CTkFrame(self, corner_radius=15)
        self.mid_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.mid_frame.grid_columnconfigure(0, weight=1)

        mid_title = ctk.CTkLabel(self.mid_frame, text="Target & Buffs Designer", font=ctk.CTkFont(size=18, weight="bold"))
        mid_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Defender Level Selector
        self.def_level_label = ctk.CTkLabel(self.mid_frame, text="Target Level: 95", font=ctk.CTkFont(size=13))
        self.def_level_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.def_level_slider = ctk.CTkSlider(self.mid_frame, from_=1, to=99, command=self._on_def_level_change)
        self.def_level_slider.set(95)
        self.def_level_slider.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Defender VIT Stat Selector
        self.vit_label = ctk.CTkLabel(self.mid_frame, text="Target VIT Stat: 80", font=ctk.CTkFont(size=13))
        self.vit_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.vit_slider = ctk.CTkSlider(self.mid_frame, from_=10, to=250, command=self._on_vit_change)
        self.vit_slider.set(80)
        self.vit_slider.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Target Resistance Dropdown
        ctk.CTkLabel(self.mid_frame, text="Target Elemental Resistance:", font=ctk.CTkFont(size=13)).grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.resist_menu = ctk.CTkOptionMenu(
            self.mid_frame,
            values=["neutral", "weak", "resist", "immune", "drain", "repel"],
            command=self._on_dropdown_change
        )
        self.resist_menu.set("neutral")
        self.resist_menu.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Defense Toggles
        ctk.CTkLabel(self.mid_frame, text="Target Defense Modifiers:", font=ctk.CTkFont(size=13)).grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")
        self.guard_var = ctk.BooleanVar(value=False)
        self.guard_check = ctk.CTkCheckBox(self.mid_frame, text="Guarding (0.8x Damage Reduction)", variable=self.guard_var, command=self._on_toggle_change)
        self.guard_check.grid(row=8, column=0, padx=20, pady=5, sticky="w")

        self.doubler_var = ctk.BooleanVar(value=False)
        self.doubler_check = ctk.CTkCheckBox(self.mid_frame, text="Doubler Passive Bug Active (Debuffed VIT -> 0.01x)", variable=self.doubler_var, command=self._on_toggle_change)
        self.doubler_check.grid(row=9, column=0, padx=20, pady=(5, 10), sticky="w")

        # Buff and Debuff Adjustments
        ctk.CTkLabel(self.mid_frame, text="Buff / Debuff Stacks:", font=ctk.CTkFont(size=15, weight="bold")).grid(row=10, column=0, padx=20, pady=(15, 5), sticky="w")

        # Attacker STR Buff Slider
        self.str_buff_label = ctk.CTkLabel(self.mid_frame, text="Attacker STR Buff: +2 (1.4x)", font=ctk.CTkFont(size=13))
        self.str_buff_label.grid(row=11, column=0, padx=20, pady=(5, 0), sticky="w")
        self.str_buff_slider = ctk.CTkSlider(self.mid_frame, from_=-3, to=3, number_of_steps=6, command=self._on_str_buff_change)
        self.str_buff_slider.set(2)
        self.str_buff_slider.grid(row=12, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Defender VIT Debuff Slider
        self.vit_buff_label = ctk.CTkLabel(self.mid_frame, text="Defender VIT Buff: -2 (0.7x)", font=ctk.CTkFont(size=13))
        self.vit_buff_label.grid(row=13, column=0, padx=20, pady=(5, 0), sticky="w")
        self.vit_buff_slider = ctk.CTkSlider(self.mid_frame, from_=-3, to=3, number_of_steps=6, command=self._on_vit_buff_change)
        self.vit_buff_slider.set(-2)
        self.vit_buff_slider.grid(row=14, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Reset Controls Button
        self.reset_btn = ctk.CTkButton(self.mid_frame, text="Reset Defaults", fg_color="#3E3E3E", hover_color="#2A2A2A", command=self.reset_defaults)
        self.reset_btn.grid(row=15, column=0, padx=20, pady=(10, 15), sticky="ew")

        # ----------------------------------------------------
        # COLUMN 2: Live Results Dashboard Panel
        # ----------------------------------------------------
        self.right_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E2E")
        self.right_frame.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(4, weight=1)  # Give Matplotlib space to expand

        right_title = ctk.CTkLabel(self.right_frame, text="Live Damage Dashboard", font=ctk.CTkFont(size=18, weight="bold"))
        right_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # 1. Normal Damage Card
        self.normal_card = ctk.CTkFrame(self.right_frame, fg_color="#2E2E3E", height=70, corner_radius=10)
        self.normal_card.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.normal_card.grid_propagate(False)
        self.normal_card.grid_columnconfigure(0, weight=1)
        self.normal_label = ctk.CTkLabel(self.normal_card, text="NORMAL DAMAGE: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A0A5E0")
        self.normal_label.grid(row=0, column=0, pady=20)

        # 2. Critical Damage Card
        self.crit_card = ctk.CTkFrame(self.right_frame, fg_color="#3E2424", height=70, corner_radius=10)
        self.crit_card.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.crit_card.grid_propagate(False)
        self.crit_card.grid_columnconfigure(0, weight=1)
        self.crit_label = ctk.CTkLabel(self.crit_card, text="CRITICAL DAMAGE: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#F87070")
        self.crit_label.grid(row=0, column=0, pady=20)

        # 3. Expected Damage Card
        self.expected_card = ctk.CTkFrame(self.right_frame, fg_color="#1E3A24", height=70, corner_radius=10)
        self.expected_card.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.expected_card.grid_propagate(False)
        self.expected_card.grid_columnconfigure(0, weight=1)
        self.expected_label = ctk.CTkLabel(self.expected_card, text="EXPECTED DAMAGE: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#80E080")
        self.expected_label.grid(row=0, column=0, pady=20)

        # 4. Interactive Matplotlib Figure Integration
        self.plot_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.plot_frame.grid(row=4, column=0, padx=10, pady=(10, 15), sticky="nsew")
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(5, 3.5), facecolor="#1E1E2E")
        self.ax.set_facecolor("#1E1E2E")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    # ----------------------------------------------------
    # Input Event Listeners
    # ----------------------------------------------------
    def _on_level_change(self, value):
        self.level_label.configure(text=f"Level: {int(value)}")
        self.update_simulation()

    def _on_str_change(self, value):
        self.str_label.configure(text=f"STR Stat: {int(value)}")
        self.update_simulation()

    def _on_mag_change(self, value):
        self.mag_label.configure(text=f"MAG Stat: {int(value)}")
        self.update_simulation()

    def _on_luc_change(self, value):
        self.luc_label.configure(text=f"LUC Stat: {int(value)}")
        self.update_simulation()

    def _on_potential_change(self, value):
        self.potential_label.configure(text=f"Skill Potential: {int(value):+d}")
        self.update_simulation()

    def _on_def_level_change(self, value):
        self.def_level_label.configure(text=f"Target Level: {int(value)}")
        self.update_simulation()

    def _on_vit_change(self, value):
        self.vit_label.configure(text=f"Target VIT Stat: {int(value)}")
        self.update_simulation()

    def _on_str_buff_change(self, value):
        val = int(value)
        mults = {-3: "0.6x", -2: "0.7x", -1: "0.85x", 0: "1.0x", 1: "1.2x", 2: "1.4x", 3: "1.6x"}
        self.str_buff_label.configure(text=f"Attacker STR Buff: {val:+d} ({mults[val]})")
        self.update_simulation()

    def _on_vit_buff_change(self, value):
        val = int(value)
        mults = {-3: "0.6x", -2: "0.7x", -1: "0.85x", 0: "1.0x", 1: "1.2x", 2: "1.4x", 3: "1.6x"}
        self.vit_buff_label.configure(text=f"Defender VIT Buff: {val:+d} ({mults[val]})")
        self.update_simulation()

    def _on_dropdown_change(self, value):
        self.update_simulation()

    def _on_toggle_change(self):
        self.update_simulation()

    def reset_defaults(self):
        self.level_slider.set(99)
        self.str_slider.set(109)
        self.mag_slider.set(109)
        self.luc_slider.set(110)
        self.potential_slider.set(9)
        self.element_menu.set("phys")
        self.power_menu.set("Heavy (120 power)")
        self.charge_var.set("impaler_glory")
        self.cz_var.set(True)
        self.mg_var.set(False)

        self.def_level_slider.set(95)
        self.vit_slider.set(80)
        self.resist_menu.set("neutral")
        self.guard_var.set(False)
        self.doubler_var.set(False)

        self.str_buff_slider.set(2)
        self.vit_buff_slider.set(-2)

        # Force visual labels updates
        self._on_level_change(99)
        self._on_str_change(109)
        self._on_mag_change(109)
        self._on_luc_change(110)
        self._on_potential_change(9)
        self._on_def_level_change(95)
        self._on_vit_change(80)
        self._on_str_buff_change(2)
        self._on_vit_buff_change(-2)

        self.update_simulation()

    # ----------------------------------------------------
    # Core Damage Calculation & Visualizer Integration
    # ----------------------------------------------------
    def update_simulation(self):
        # 1. Read input parameters from panels
        attacker_lv = int(self.level_slider.get())
        attacker_stats = {
            'STR': int(self.str_slider.get()),
            'VIT': 80,
            'MAG': int(self.mag_slider.get()),
            'AGI': 70,
            'LUC': int(self.luc_slider.get())
        }
        potentials = {self.element_menu.get(): int(self.potential_slider.get())}
        
        charge = self.charge_var.get()
        charge_state = None if charge == "none" else charge
        
        passives = []
        if self.cz_var.get():
            passives.append("critical_zealot")
        if self.mg_var.get():
            passives.append("murderous_glee")

        # Instantiate Attacker
        attacker = Combatant(
            name="Nahobino",
            base_stats=attacker_stats,
            level=attacker_lv,
            skill_potentials=potentials,
            charge_state=charge_state,
            passive_abilities=passives
        )
        # Apply Attacker STR Buff
        attacker.buff_levels['STR'] = int(self.str_buff_slider.get())

        # Instantiate Defender
        defender_lv = int(self.def_level_slider.get())
        defender_stats = {
            'STR': 40,
            'VIT': int(self.vit_slider.get()),
            'MAG': 40,
            'AGI': 60,
            'LUC': 64
        }
        defender = Combatant(
            name="Target",
            base_stats=defender_stats,
            level=defender_lv,
            guarding=self.guard_var.get(),
            doubler_active=self.doubler_var.get()
        )
        # Apply Defender VIT Debuff
        defender.buff_levels['VIT'] = int(self.vit_buff_slider.get())

        # Map selected skill power preset
        power_map = {
            "Light (30 power)": 30,
            "Medium (70 power)": 70,
            "Heavy (120 power)": 120,
            "Severe (200 power)": 200
        }
        self.engine.skill_power = power_map[self.power_menu.get()]

        # 2. Run deterministic core simulation (excluding stochastic variance for UI cleanliness)
        # Temporarily mock stochastic variance methods to return base values for deterministic visual feedback
        original_apply_variance = self.engine._apply_variance
        self.engine._apply_variance = lambda base_damage: base_damage

        # Calculate exact hit damages
        element = self.element_menu.get()
        resistance = self.resist_menu.get()

        normal_dmg = self.engine.calculate_vengeance_damage(
            attacker=attacker, defender=defender,
            skill_element=element, resistance=resistance, is_crit=False
        )

        crit_dmg = self.engine.calculate_vengeance_damage(
            attacker=attacker, defender=defender,
            skill_element=element, resistance=resistance, is_crit=True
        )

        # Compute accurate crit rate
        crit_rate = self.engine.calculate_crit_rate(attacker, defender)
        # Apply passives to crit rate
        damage_state = {"crit_rate": crit_rate}
        damage_state = self.engine._apply_passives(attacker.passive_abilities, damage_state)
        
        final_crit_rate = crit_rate
        if "crit_rate_mult" in damage_state:
            final_crit_rate *= damage_state["crit_rate_mult"]
        final_crit_rate = max(0.0, min(1.0, final_crit_rate))

        expected_dmg = normal_dmg * (1.0 - final_crit_rate) + crit_dmg * final_crit_rate

        # Restore original variance method
        self.engine._apply_variance = original_apply_variance

        # Update Live result label cards
        self.normal_label.configure(text=f"NORMAL DAMAGE: {normal_dmg:.1f}")
        self.crit_label.configure(text=f"CRITICAL DAMAGE: {crit_dmg:.1f}")
        self.expected_label.configure(text=f"EXPECTED DAMAGE: {expected_dmg:.1f} (Crit Rate: {final_crit_rate*100:.1f}%)")

        # 3. Re-render Matplotlib Line Graph inside panel
        self.ax.clear()
        
        # Calculate progressive damage values across Attacker STR Buff range (-3 to +3)
        buff_levels = list(range(-3, 4))
        progressive_damages = []
        
        # Save current STR buff state to temporarily progressive check
        orig_str_buff = attacker.buff_levels['STR']
        self.engine._apply_variance = lambda base_damage: base_damage  # Det var

        for buff in buff_levels:
            attacker.buff_levels['STR'] = buff
            dmg = self.engine.calculate_vengeance_damage(
                attacker=attacker, defender=defender,
                skill_element=element, resistance=resistance, is_crit=False
            )
            progressive_damages.append(dmg)

        # Restore states
        attacker.buff_levels['STR'] = orig_str_buff
        self.engine._apply_variance = original_apply_variance

        # Plot progressive curve
        self.ax.plot(buff_levels, progressive_damages, color="#58A6FF", marker="o", linewidth=2, label="Normal Damage")
        
        # Highlight current selected STR buff state
        current_str_buff = int(self.str_buff_slider.get())
        self.ax.axvline(x=current_str_buff, color="#FF7F7F", linestyle="--", linewidth=1.5, label=f"Current Buff ({current_str_buff:+d})")
        
        # Style the Plot
        self.ax.set_title("Damage vs STR Buff Scaling", color="white", fontsize=10, fontweight="bold")
        self.ax.set_xlabel("STR Buff level", color="white", fontsize=8)
        self.ax.set_ylabel("Damage", color="white", fontsize=8)
        self.ax.tick_params(colors="white", labelsize=8)
        self.ax.grid(True, color="#2E2E3E", alpha=0.5)
        self.ax.legend(loc="upper left", facecolor="#1E1E2E", edgecolor="#2E2E3E", fontsize=7, labelcolor="white")
        
        # Spacing adjustment
        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = SMTV_GUI()
    app.mainloop()
