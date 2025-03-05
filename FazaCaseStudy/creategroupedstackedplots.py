import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# Define the scenario comparisons (each list represents a group to compare)
comparisons = {
    #"Demand": ["lowdemand", "basecase", "highdemand"],
    #"RESComparison": ["bestcaseres", "basecase", "worstcaseres"],
    #"RESComparisonNoSubsystem": ["bestcaseresnosubsystem", "basecasenosubsystem", "worstcaseresnosubsystem"]
    "LPvsMILP": ["basecasenosubsystem", "basecaseLP"]
}

scenario_names = {
    "lowdemand": "Low Demand",
    "basecase": "Base Case",
    "highdemand": "High Demand",
    "bestcaseres": "RES Best Case",
    "worstcaseres": "RES Worst Case",
    "bestcaseresnosubsystem": "RES Best Case without Subsystem",
    "basecasenosubsystem": "Base Case without Subsystem",
    "worstcaseresnosubsystem": "RES Worst Case without Subsystem",
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

# Define color mapping
production_colors = {
    'Solar PV Production': '#FFC107',
    'Wind Production': '#03A9F4',
    'Diesel Generator Production': '#8B4513',
    'Battery Outflow': '#4CAF50'
}

demand_color = '#000000'

# Define transformation loss and curtailment patterns
loss_pattern = {'hatch': '//', 'color': 'red', 'linewidth': 2}
curtailment_pattern = {'hatch': '//', 'color': 'grey', 'linewidth': 2}

step_years = 5
base_year = 2022  # Reference year for steps

for comparison_name, scenario_group in comparisons.items():

    print(f"Processing comparison: {comparison_name} - {scenario_group}")

    # Initialize storage for all scenarios
    all_scenario_data = {scenario: {} for scenario in scenario_group}
    max_steps = 0
    global_max_y, global_min_y = float('-inf'), float('inf')

    for scenario in scenario_group:
        print(f"Processing scenario: {scenario}")

        # Path to the Excel file
        file_path = f'FazaCaseStudy//{scenario}//results//Energy Balance - Scenario 1.xlsx'
        data = pd.ExcelFile(file_path)

        cumulative_data_per_step = {}
        i = 0

        for sheet_name in data.sheet_names:
            df = data.parse(sheet_name)
            df = df.loc[:, ~df.columns.str.contains('Total Production', case=False)]
            df = df.drop(columns=['Battery State of Charge (%)', 'DC System Feed In Losses', 'DC System Charge Losses'], errors='ignore')
            df.columns = df.columns.str.replace('Actual Production', 'Production', case=False)
            df.columns = df.columns.str.replace(' \(kWh\)', '', regex=True)

            # Handle Curtailments
            mask = df['Solar PV Production'] <= 0
            df.loc[mask, 'Solar PV Curtailment'] += df.loc[mask, 'Solar PV Production']
            df.loc[mask, 'Solar PV Production'] = 0
            mask = df['Wind Production'] <= 0
            df.loc[mask, 'Wind Curtailment'] += df.loc[mask, 'Wind Production']
            df.loc[mask, 'Wind Production'] = 0

            year = base_year + i
            print(year)
            i += 1
            start_time = f'{year}-01-01 00:00:00'
            end_time = f'{year}-12-31 23:00:00'
            date_range = pd.date_range(start=start_time, end=end_time, freq='h')
            date_range = date_range[~((date_range.month == 2) & (date_range.day == 29))]
            df.index = date_range
            
            # Calculate hourly averages
            hourly_avg = df.groupby(df.index.hour).mean()

            # Determine step
            step = ((year - base_year) // step_years) + 1
            max_steps = max(max_steps, step)

            if step not in cumulative_data_per_step:
                cumulative_data_per_step[step] = []

            cumulative_data_per_step[step].append(hourly_avg)

        all_scenario_data[scenario] = cumulative_data_per_step

    # Determine global min/max for y-axis consistency
    for scenario, step_data in all_scenario_data.items():
        for step, data_list in step_data.items():
            step_avg = pd.concat(data_list).groupby(level=0).mean()
            total_positive = step_avg[list(production_colors.keys())].sum(axis=1)

            for prod_col in production_colors.keys():
                curtail_col = prod_col.replace("Production", "Curtailment")
                if curtail_col == "Battery Outflow":
                    curtail_col = None 
                if curtail_col in step_avg.columns:
                    total_positive += step_avg[curtail_col]

            if 'Demand' in step_avg.columns:
                total_positive = pd.concat([total_positive, step_avg['Demand']], axis=1).max(axis=1)

            total_negative = pd.Series(0, index=step_avg.index)
            for prod_col in production_colors.keys():
                loss_col = prod_col.replace("Production", "Transformation Losses")
                if prod_col == 'Battery Outflow':
                    loss_col = 'Battery Transformation Losses'
                    if loss_col not in step_avg.columns:
                        loss_col = 'DC System Transformation Losses'
                if loss_col in step_avg.columns:
                    total_negative -= step_avg[loss_col]

            if 'Battery Inflow' in step_avg.columns:
                total_negative -= step_avg['Battery Inflow']

            global_max_y = max(global_max_y, total_positive.max())
            global_min_y = min(global_min_y, total_negative.min())

    # Create subplot grid
    fig, axs = plt.subplots(max_steps, len(scenario_group), figsize=(5 * len(scenario_group), 3 * max_steps), sharex=True, sharey=True)

    all_labels, all_patches = [], []

    for col_idx, scenario in enumerate(scenario_group):
        for row_idx in range(max_steps):
            step = row_idx + 1
            ax = axs[row_idx, col_idx] if len(scenario_group) > 1 else axs[row_idx]

            if step in all_scenario_data[scenario]:
                step_avg = pd.concat(all_scenario_data[scenario][step]).groupby(level=0).mean()

                bottom_stack = pd.Series(0, index=step_avg.index)
                negative_stack = pd.Series(0, index=step_avg.index)

                for column in production_colors.keys():
                    if column in step_avg.columns:
                        bar = ax.bar(step_avg.index, step_avg[column], bottom=bottom_stack,
                                    color=production_colors[column], label=column)
                        bottom_stack += step_avg[column]
                        if column == "Battery Outflow":
                            column = "Battery"
                        if column not in all_labels:
                            all_labels.append(column)
                            all_patches.append(bar[0])

                for prod_col in production_colors.keys():
                    curtail_col = prod_col.replace("Production", "Curtailment")
                    if curtail_col == "Battery Outflow":
                        curtail_col = None 
                    if curtail_col in step_avg.columns:
                        bar = ax.bar(step_avg.index, step_avg[curtail_col], bottom=bottom_stack,
                                    color=production_colors[prod_col], edgecolor=curtailment_pattern['color'],
                                    hatch=curtailment_pattern['hatch'], label=curtail_col)
                        bottom_stack += step_avg[curtail_col]
                        if curtail_col not in all_labels:
                            all_labels.append(curtail_col)
                            all_patches.append(bar[0])
        
                if 'Battery Inflow' in step_avg.columns:
                    ax.bar(step_avg.index, -step_avg['Battery Inflow'], bottom=negative_stack, color=production_colors['Battery Outflow'], label='Battery Inflow')
                    negative_stack -= step_avg['Battery Inflow']

                for prod_col in production_colors.keys():
                    loss_col = prod_col.replace("Production", "Transformation Losses")
                    if loss_col in step_avg.columns:
                        if 'Transformation Losses' in loss_col:
                            loss_bar = ax.bar(step_avg.index, -step_avg[loss_col], bottom=negative_stack, color=production_colors[prod_col], edgecolor=loss_pattern['color'], hatch=loss_pattern['hatch'], label=loss_col)
                            negative_stack -= step_avg[loss_col]
                            if loss_col not in all_labels:
                                all_labels.append(loss_col)
                                all_patches.append(loss_bar[0])                            
                if 'DC System Transformation Losses' in step_avg.columns:
                    loss_bar = ax.bar(step_avg.index, -step_avg['DC System Transformation Losses'], bottom=negative_stack, color=production_colors['Battery Outflow'], edgecolor=loss_pattern['color'], hatch=loss_pattern['hatch'], label='DC System Transformation Losses')
                    negative_stack -= step_avg['DC System Transformation Losses']
                    if 'DC System Transformation Losses' not in all_labels:
                        all_labels.append('DC System Transformation Losses')
                        all_patches.append(loss_bar[0])

                if 'Demand' in step_avg.columns:
                    demand_line, = ax.plot(step_avg.index, step_avg['Demand'], color=demand_color, label='Demand', linewidth=2)
                    if 'Demand' not in all_labels:
                        all_labels.append('Demand')
                        all_patches.append(demand_line)

            ax.set_ylim(global_min_y * 1.1, global_max_y * 1.1)
            ax.set_title(f"{scenario_names[scenario]} - Step {step}")
            ax.grid(True)

    fig.supxlabel("Hour of Day")
    fig.supylabel("Energy (kWh)")

    fig.legend(all_patches, all_labels, loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=len(all_labels)/3, frameon=False)

    plt.tight_layout(rect=[0, 0, 0.85, 0.95])

    output_dir = f'FazaCaseStudy//plots//comparisons'
    plt.savefig(f"{output_dir}/{comparison_name}_energy_balance_comparison.png", bbox_inches='tight', facecolor="white", edgecolor="white")
    plt.close()

    print(f'Finished comparison: {comparison_name}')
