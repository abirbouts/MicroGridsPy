import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

scenarios = ["basecasenodrivetraineff", "basecaseLP", "basecase", "basecasenosubsystem", "bestcaseres", "worstcaseres", "highdemand", "lowdemand", "bestcaseresnosubsystem", "worstcaseresnosubsystem", "basecasenasa"]
comparisons = {
    "Demand": ["lowdemand", "basecase", "highdemand"],
    "RESComparison": ["bestcaseres", "basecase", "worstcaseres"],
    "RESComparisonNoSubsystem": ["bestcaseresnosubsystem", "basecasenosubsystem", "worstcaseresnosubsystem"]
}

plt.style.use('fivethirtyeight')
textwidthfraction = 0.9
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

for i in range(len(scenarios)):
    scenario = scenarios[i]
    print(scenario)

    file_path = f'FazaCaseStudy\\{scenario}\\results\\Sizing Results.xlsx'

    base_colors = {
        'Solar PV': '#FFC107',
        'Wind': '#03A9F4',
        'Diesel Generator': '#8B4513',
        'Battery' : '#4CAF50'
    }

    hatch_patterns = {
        'Step 1': '||',
        'Step 2': '--',
        'Step 3': '//',
        'Step 4': 'xx'
    }

    def load_data(file_path):
        df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl')
        df.set_index('Component', inplace=True)
        df.index = df.index.str.replace(r" \((kWh|kW)\)", "", regex=True)
        cols = list(df.columns)
        for i in range(len(cols) - 1, 1, -1):
            df[cols[i]] = df[cols[i]] - df[cols[i - 1]]
        
        return df


    def create_stacked_bar_chart(df):
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()
        bottom_stack = pd.Series(0, index=df.index)
        bottom_stack_battery = 0

        if 'Existing' in df.columns:
            for idx, comp in enumerate(df.index):
                if comp == 'Battery':
                    ax2.bar(comp, df.loc[comp, 'Existing'], color=base_colors[comp], edgecolor='black', label='Existing')
                    bottom_stack_battery += df.loc[comp, 'Existing']
                else:
                    ax1.bar(comp, df.loc[comp, 'Existing'], color=base_colors[comp], edgecolor='black', label='Existing')
                    bottom_stack[comp] += df.loc[comp, 'Existing']

        for step, hatch_pattern in hatch_patterns.items():
            if step in df.columns:
                for idx, comp in enumerate(df.index):
                    if comp == 'Battery':
                        ax2.bar(comp, df.loc[comp, step], bottom=bottom_stack_battery, color=base_colors[comp],
                                edgecolor='black', hatch=hatch_pattern)
                        bottom_stack_battery += df.loc[comp, step]
                    else:
                        ax1.bar(comp, df.loc[comp, step], bottom=bottom_stack[comp], color=base_colors[comp],
                                edgecolor='black', hatch=hatch_pattern)
                        bottom_stack[comp] += df.loc[comp, step]

        legend_elements = [
            Patch(facecolor='white', edgecolor='black', label='Existing')
        ] + [
            Patch(facecolor='white', edgecolor='black', hatch=hatch_patterns[step], label=step)
            for step in hatch_patterns
        ]
    
        ax1.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.2, 1), title="Investment Steps")
        ax1.set_ylabel("Capacity (kW)")
        ax2.set_ylabel("Battery Capacity (kWh)")

        ax1.set_ylim(0,4000)
        ax2.set_ylim(0,16000)

        ylim1 = ax1.get_ylim()
        ylim2 = ax2.get_ylim()
        num_ticks = 5
        yticks1 = np.linspace(ylim1[0], ylim1[1], num_ticks)
        yticks2 = np.linspace(ylim2[0], ylim2[1], num_ticks)
        ax1.set_yticks(yticks1)
        ax2.set_yticks(yticks2)

        ax1.grid(True)
        ax2.grid(False) 

        ax2.set_position([ax2.get_position().x0, ax2.get_position().y0, ax2.get_position().width * 0.9, ax2.get_position().height])
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        plt.tight_layout(rect=[0, 0, 0.8, 1])
        plt.savefig(f'FazaCaseStudy\\{scenario}\\plots\\{scenario}_system_sizing.png', bbox_inches='tight', facecolor="white", edgecolor="white")

    df = load_data(file_path)
    create_stacked_bar_chart(df)
    print(f'Sizing plot created for {scenario}')
