import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import os

# Define comparisons
comparisons = {
    #"Demand": ["lowdemand", "basecase", "highdemand"],
    "RESComparison": ["bestcaseres", "basecase", "worstcaseres"],
    "RESComparisonNoSubsystem": ["bestcaseresnosubsystem", "basecasenosubsystem", "worstcaseresnosubsystem"],
    #"NasavsPVGIS": ["basecase", "basecasenasa"],
    #"LPvsMILP": ["basecasenosubsystem", "basecaseLP"]
}

scenario_names = {
    "lowdemand": "Low Demand",
    "basecase": "Base Case",
    "highdemand": "High Demand",
    "bestcaseres": "RES Best Case",
    "worstcaseres": "RES Worst Case",
    "bestcaseresnosubsystem": "RES Best Case No Subsystem",
    "basecasenosubsystem": "Base Case No Subsystem",
    "worstcaseresnosubsystem": "RES Worst Case No Subsystem",
    "basecasenasa": "NASA Data",
    "basecaseLP": "Base Case LP"
}

plt.style.use('fivethirtyeight')
textwidthfraction = 0.7
fontsize = 12 / textwidthfraction
fontsize2 = 10 / textwidthfraction
plt.rcParams.update({
    "text.usetex": True,      
    "font.family": "serif",
    "font.size": fontsize,
    "axes.titlesize": fontsize,
    "axes.labelsize": fontsize,
    "legend.fontsize": fontsize,
    "xtick.labelsize": fontsize2,
    "ytick.labelsize": fontsize2,
    "hatch.linewidth": 3.0
})

# Color mapping for different components
base_colors = {
    'Solar PV': '#FFC107',
    'Wind': '#03A9F4',
    'Diesel Generator': '#8B4513',
    'Battery': '#4CAF50'
}

# Hatching patterns for investment steps
hatch_patterns = {
    'Step 1': '||',
    'Step 2': '--',
    'Step 3': '//',
    'Step 4': 'xx'
}

# Outline colors for scenarios
scenario_colors = ['#E57373', '#64B5F6', '#81C784']  # Red, Blue, Green

def load_data(file_path):
    """Load and process sizing data from Excel"""
    df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl')
    df.set_index('Component', inplace=True)
    df.index = df.index.str.replace(r" \((kWh|kW)\)", "", regex=True)
    cols = list(df.columns)
    for i in range(len(cols) - 2, 1, -1):  # Start from last column, subtract previous one
        df[cols[i]] = df[cols[i]] - df[cols[i - 1]]
    
    return df 


def create_comparison_stacked_bar_chart(comparison_name, scenarios):
    """Create a stacked bar chart comparing multiple scenarios in a given category"""
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    width = 0.18  # Bar width for individual scenarios
    spacing = 0.05  # Space between scenario groups
    x_positions = np.arange(len(base_colors))  # X-axis positions for each component

    # Legend elements
    legend_elements = [Patch(facecolor='white', edgecolor='black', label='Existing')] + [
        Patch(facecolor='white', edgecolor='black', hatch=hatch_patterns[step], label=step) for step in hatch_patterns
    ]

    scenario_legend_elements = [
        Patch(facecolor='white', edgecolor=scenario_colors[i], linewidth=3, label=scenario_names[scenarios[i]]) for i in range(len(scenarios))
    ]

    for i, scenario in enumerate(scenarios):
        file_path = f'FazaCaseStudy\\{scenario}\\results\\Sizing Results.xlsx'
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        
        df = load_data(file_path)



        bottom_stack = pd.Series(0, index=df.index)
        bottom_stack_battery = 0

        shift = (i - 1) * (width + spacing)  # Adjust positioning for each scenario with spacing

        # Plot existing components
        if 'Existing' in df.columns:
            for comp in df.index:
                xpos = x_positions[df.index.get_loc(comp)] + shift
                if comp == 'Battery':
                    ax2.bar(xpos, df.loc[comp, 'Existing'],
                            color=base_colors[comp], edgecolor='black', width=width)
                    bottom_stack_battery += df.loc[comp, 'Existing']
                else:
                    ax1.bar(xpos, df.loc[comp, 'Existing'],
                            color=base_colors[comp], edgecolor='black', width=width)
                    bottom_stack[comp] += df.loc[comp, 'Existing']

        # Plot investment steps with hatch
        for step, hatch_pattern in hatch_patterns.items():
            if step in df.columns:
                for comp in df.index:
                    xpos = x_positions[df.index.get_loc(comp)] + shift
                    if comp == 'Battery':
                        ax2.bar(xpos, df.loc[comp, step],
                                bottom=bottom_stack_battery, color=base_colors[comp],
                                edgecolor='black', hatch=hatch_pattern, width=width)
                        bottom_stack_battery += df.loc[comp, step]
                    else:
                        ax1.bar(xpos, df.loc[comp, step],
                                bottom=bottom_stack[comp], color=base_colors[comp],
                                edgecolor='black', hatch=hatch_pattern, width=width)
                        bottom_stack[comp] += df.loc[comp, step]

        # Overlay the colored border bars (same position & height as stacked bars, no extra height)
        for comp in df.index:
            xpos = x_positions[df.index.get_loc(comp)] + shift
            if comp == 'Battery':
                ax2.bar(xpos, bottom_stack_battery, bottom=0,  # Same height as stacked bars
                        color='none', edgecolor=scenario_colors[i], linewidth=5, width=width)
            else:
                ax1.bar(xpos, bottom_stack[comp], bottom=0,  # Same height as stacked bars
                        color='none', edgecolor=scenario_colors[i], linewidth=5, width=width)

    # Formatting
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(base_colors.keys(), rotation=45, ha='right')
    ax1.set_ylabel("Capacity (kW)")
    ax2.set_ylabel("Battery Capacity (kWh)")

    # Scale axes
    ax1.set_ylim(0, 4000)
    ax2.set_ylim(0, 16000)
    
    ylim1, ylim2 = ax1.get_ylim(), ax2.get_ylim()
    yticks1, yticks2 = np.linspace(ylim1[0], ylim1[1], 5), np.linspace(ylim2[0], ylim2[1], 5)
    ax1.set_yticks(yticks1)
    ax2.set_yticks(yticks2)
    
    ax1.grid(True)
    ax2.grid(False)

    # Add legends
    ax1.legend(handles=legend_elements + scenario_legend_elements, loc='upper left', bbox_to_anchor=(1.1, 1))

    output_dir = f'FazaCaseStudy\\plots\\comparisons'
    plt.savefig(f'{output_dir}\\{comparison_name}_comparison_sizing.png', bbox_inches='tight', facecolor="white", edgecolor="white")
    plt.close()

    print(f'Sizing comparison plot created for {comparison_name}')


# Run comparison for each category
for comparison_name, scenario_list in comparisons.items():
    create_comparison_stacked_bar_chart(comparison_name, scenario_list)
