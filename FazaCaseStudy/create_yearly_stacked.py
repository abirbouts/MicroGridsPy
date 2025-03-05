import pandas as pd
import matplotlib.pyplot as plt
import os

scenarios = ["basecasenodrivetraineff", "basecaseLP", "basecase", "basecasenosubsystem", "bestcaseres", "worstcaseres", "highdemand", "lowdemand", "bestcaseresnosubsystem", "worstcaseresnosubsystem", "basecasenasa"]

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

    # Path to the Excel file
    file_path = f'FazaCaseStudy//{scenario}//results//Energy Balance - Scenario 1.xlsx'

    # Load the Excel file with multiple sheets
    data = pd.ExcelFile(file_path)

    # Output directory for saving plots
    output_dir = f'FazaCaseStudy//{scenario}//plots'
    os.makedirs(output_dir, exist_ok=True)

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

    step_years = 5  # Group years into 5-year steps
    i = 0
    cumulative_data_per_step = {}
    current_step_data = []
    global_max_y = float('-inf')  # Initialize for maximum y-axis scaling
    global_min_y = float('inf')   # Initialize for minimum y-axis scaling

    # Process each year
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

        year = 2022 + i
        print(year)
        i += 1
        start_time = f'{year}-01-01 00:00:00'
        end_time = f'{year}-12-31 23:00:00'
        date_range = pd.date_range(start=start_time, end=end_time, freq='h')
        date_range = date_range[~((date_range.month == 2) & (date_range.day == 29))]
        df.index = date_range

        # Calculate average hourly values
        hourly_avg = df.groupby(df.index.hour).mean()

        # Determine current step
        step = ((year - 2022) // step_years) + 1
        if step not in cumulative_data_per_step:
            cumulative_data_per_step[step] = []

        cumulative_data_per_step[step].append(hourly_avg)

    # First loop to find global max and min y-values for consistent scaling
    for step, data_list in cumulative_data_per_step.items():
        step_avg = pd.concat(data_list).groupby(level=0).mean()

        # Positive stack for production, curtailments, and demand
        total_positive = step_avg[list(production_colors.keys())].sum(axis=1)

        # Include curtailments
        for prod_col in production_colors.keys():
            curtail_col = prod_col.replace("Production", "Curtailment")
            if curtail_col == "Battery Outflow":
                curtail_col = None 
            if curtail_col in step_avg.columns:
                total_positive += step_avg[curtail_col]

        # Include demand for comparison
        if 'Demand' in step_avg.columns:
            total_positive = pd.concat([total_positive, step_avg['Demand']], axis=1).max(axis=1)

        # Negative stack for inflows and transformation losses
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

        # Update global min and max
        global_max_y = max(global_max_y, total_positive.max())
        global_min_y = min(global_min_y, total_negative.min())

    # Plot for each step in a 2x2 combined plot
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))  # 4 subplots for 4 steps

    all_labels = []
    all_patches = []

    # Second loop to plot each step
    for idx, (step, data_list) in enumerate(cumulative_data_per_step.items()):
        step_avg = pd.concat(data_list).groupby(level=0).mean()
        row, col = divmod(idx, 2)
        ax = axs[row, col]

        # Prepare data for stacked bar plot
        bottom_stack = pd.Series(0, index=step_avg.index)
        negative_stack = pd.Series(0, index=step_avg.index)

        # Positive bars for production
        for column in production_colors.keys():
            if column in step_avg.columns:
                bar = ax.bar(step_avg.index, step_avg[column], bottom=bottom_stack,
                            color=production_colors[column], label=column)
                bottom_stack += step_avg[column]
                if column not in all_labels:
                    all_labels.append(column)
                    all_patches.append(bar[0])

        # Curtailments as striped positive bars
        for prod_col in production_colors.keys():
            curtail_col = prod_col.replace("Production", "Curtailment")
            if curtail_col == 'Battery Outflow':
                curtail_col = None
            if curtail_col in step_avg.columns:
                bar = ax.bar(step_avg.index, step_avg[curtail_col], bottom=bottom_stack,
                            color=production_colors[prod_col], edgecolor=curtailment_pattern['color'],
                            hatch=curtailment_pattern['hatch'], label=curtail_col)
                bottom_stack += step_avg[curtail_col]
                if curtail_col not in all_labels:
                    all_labels.append(curtail_col)
                    all_patches.append(bar[0])

        # Negative bars for battery inflows and transformation losses
        if 'Battery Inflow' in step_avg.columns:
            inflow_bar = ax.bar(step_avg.index, -step_avg['Battery Inflow'], bottom=negative_stack,
                                color=production_colors['Battery Outflow'], label='Battery Inflow')
            negative_stack -= step_avg['Battery Inflow']
            if 'Battery Inflow' not in all_labels:
                all_labels.append('Battery Inflow')
                all_patches.append(inflow_bar[0])

        for prod_col in production_colors.keys():
            loss_col = prod_col.replace("Production", "Transformation Losses")
            if prod_col == 'Battery Outflow':
                loss_col = 'Battery Transformation Losses'
                if loss_col not in step_avg.columns:
                    loss_col = 'DC System Transformation Losses'
            if loss_col in step_avg.columns:
                loss_bar = ax.bar(step_avg.index, -step_avg[loss_col], bottom=negative_stack,
                                color=production_colors[prod_col], edgecolor=loss_pattern['color'],
                                hatch=loss_pattern['hatch'], label=loss_col)
                negative_stack -= step_avg[loss_col]
                if loss_col not in all_labels:
                    all_labels.append(loss_col)
                    all_patches.append(loss_bar[0])

        # Plot demand as a line plot
        if 'Demand' in step_avg.columns:
            demand_line, = ax.plot(step_avg.index, step_avg['Demand'], color=demand_color, label='Demand', linewidth=2)
            if 'Demand' not in all_labels:
                all_labels.append('Demand')
                all_patches.append(demand_line)

        # Apply consistent y-axis scaling using global min and max
        ax.set_ylim(global_min_y * 1.1, global_max_y * 1.1)
        ax.set_title(f"Step {step}")
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Energy [kWh]")
        ax.grid(True)

    # Create shared legend on the right side
    fig.legend(all_patches, all_labels, loc='center left', bbox_to_anchor=(0.85, 0.5), fontsize=12, frameon=False)

    plt.tight_layout(rect=[0, 0, 0.85, 0.95])  # Adjust layout for right-side legend

    # Save combined plot
    plt.savefig(f"{output_dir}/{scenario}_combined_energy_balance.png", facecolor="white", edgecolor="white")
    plt.close()

    print(f'Finished step-wise plotting with consistent y-axis and right-side legend for {scenario}')
