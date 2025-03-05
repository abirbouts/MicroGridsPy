import pandas as pd
import matplotlib.pyplot as plt
import os

# Scenarios that should be compared
comparisons = {
    #"Demand": ["lowdemand", "basecase", "highdemand"],
    #"RESComparison": ["bestcaseres", "basecase", "worstcaseres"],
    #"RESComparisonNoSubsystem": ["bestcaseresnosubsystem", "basecasenosubsystem", "worstcaseresnosubsystem"],
    "LPvsMILP": ["basecasenosubsystem", "basecaseLP"]
}

scenario_names = {
    "lowdemand": "Low Demand",
    "basecase": "Base Case",
    "highdemand": "High Demand",
    "bestcaseres": "RES Best Case",
    "worstcaseres": "RES Worst Case",
    "bestcaseresnosubsystem": "RES Best Case",
    "basecasenosubsystem": "Base Case MILP",
    "worstcaseresnosubsystem": "RES Worst Case",
    "basecasenasa": "NASA Data",
    "basecaseLP": "Base Case LP"
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
    "ytick.labelsize": fontsize2
})

# Define color mapping
production_colors = {
    'Solar PV Production': '#FFC107',
    'Wind Production': '#03A9F4',
    'Diesel Generator Production': '#8B4513',
}

step_years = 5  # Group data into five-year steps
base_year = 2022  # Start year

for comparison_name, scenario_group in comparisons.items():

    print(f"Processing comparison: {comparison_name} - {scenario_group}")

    # Initialize a dictionary to store all step data for all scenarios
    all_scenario_data = {scenario: {} for scenario in scenario_group}
    max_steps = 0

    for scenario in scenario_group:
        print(f"Processing scenario: {scenario}")

        # Path to the Excel file
        file_path = f'FazaCaseStudy//{scenario}//results//Energy Balance - Scenario 1.xlsx'

        # Load the Excel file
        data = pd.ExcelFile(file_path)

        # Store cumulative production for each step
        cumulative_data = pd.DataFrame()
        step_data = {}
        i = 0

        for sheet_name in data.sheet_names:
            df = data.parse(sheet_name)
            df = df.loc[:, ~df.columns.str.contains('Total Production', case=False)]
            df = df.drop(columns=['Battery State of Charge (%)', 'DC System Feed In Losses', 'DC System Charge Losses'], errors='ignore')
            df.columns = df.columns.str.replace('Actual Production', 'Production', case=False)
            df.columns = df.columns.str.replace(' \(kWh\)', '', regex=True)

            mask = df['Solar PV Production'] <= 0
            df.loc[mask, 'Solar PV Curtailment'] += df.loc[mask, 'Solar PV Production']
            df.loc[mask, 'Solar PV Production'] = 0
            mask = df['Wind Production'] <= 0
            df.loc[mask, 'Wind Curtailment'] += df.loc[mask, 'Wind Production']
            df.loc[mask, 'Wind Production'] = 0

            year = base_year + i
            i += 1
            print(year)
            # Add to cumulative data
            cumulative_data = cumulative_data.add(df, fill_value=0) if not cumulative_data.empty else df

            # Generate a data entry for each step
            if (year - base_year + 1) % step_years == 0 or sheet_name == data.sheet_names[-1]:
                step = (year - base_year) // step_years + 1
                max_steps = max(max_steps, step)

                # Calculate total production for each resource
                total_production = {col: cumulative_data[col].sum() for col in production_colors.keys() if cumulative_data[col].sum() > 0}

                # Store for combined plot
                step_data[step] = total_production

                # Reset cumulative data for next step
                cumulative_data = pd.DataFrame()

        all_scenario_data[scenario] = step_data

    # Plotting all steps for the scenarios
    fig, axs = plt.subplots(max_steps, len(scenario_group), figsize=(4 * len(scenario_group), 3 * max_steps), sharey=True)

    if max_steps == 1:
        axs = [axs]

    for col_idx, scenario in enumerate(scenario_group):
        for row_idx in range(max_steps):
            step = row_idx + 1

            ax = axs[row_idx, col_idx] if len(scenario_group) > 1 else axs[row_idx]
            if step in all_scenario_data[scenario]:
                total_production = all_scenario_data[scenario][step]

                labels = list(total_production.keys())
                values = list(total_production.values())
                colors = [production_colors[label] for label in labels]

                wedges, texts, autotexts = ax.pie(
                    values,
                    labels=None,
                    colors=colors,
                    autopct='%1.1f%%',
                    startangle=140
                )

                ax.set_title(f"{scenario_names[scenario]} - Step {step}", pad=5)

    # Create a single shared legend
    fig.legend(
        handles=[plt.Line2D([0], [0], marker='o', color='w', markersize=10, markerfacecolor=production_colors[key]) for key in production_colors.keys()],
        labels=list(production_colors.keys()),
        loc='lower center',
        ncol=len(production_colors),
        frameon=False
    )

    plt.tight_layout(rect=[0, 0.05, 1, 0.95]) 
    output_dir = f'FazaCaseStudy//plots//comparisons'
    plt.savefig(f"{output_dir}/{comparison_name}_comparison.png", bbox_inches='tight', facecolor="white", edgecolor="white")
    plt.close()

    print(f'Finished plotting comparison: {comparison_name}')
