import pandas as pd
import matplotlib.pyplot as plt
import os

scenarios = ["basecasenodrivetraineff", "basecaseLP","basecase", "basecasenosubsystem", "bestcaseres", "worstcaseres", "highdemand", "lowdemand", "bestcaseresnosubsystem", "worstcaseresnosubsystem", "basecasenasa"]

comparisons = {
    "Demand": ["lowdemand", "basecase", "highdemand"],
    "RES": ["bestcaseres", "basecase", "worstcaseres"],
    "RESNosubsystem": ["bestcaseresnosubsystem", "basecasenosubsystem", "worstcaseresnosubsystem"]
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
    }

    step_years = 5  # Group data into five-year steps
    i = 0

    # Initialize cumulative data for each step
    cumulative_data = pd.DataFrame()

    # Store pie chart data for the combined plot
    combined_pie_data = {}

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

        year = 2022 + i
        i += 1
        print(year)

        # Add to cumulative data
        cumulative_data = cumulative_data.add(df, fill_value=0) if not cumulative_data.empty else df

        # Generate a pie chart every 5 years
        if (year - 2022 + 1) % step_years == 0 or sheet_name == data.sheet_names[-1]:
            step = (year - 2022) // step_years + 1
            print(f"Creating plot for Step {step}")

            # Calculate total production for each resource
            total_production = {column: cumulative_data[column].sum() for column in production_colors.keys() if cumulative_data[column].sum() > 0}

            # Prepare pie chart data
            labels = list(total_production.keys())
            values = list(total_production.values())
            colors = [production_colors[label] for label in labels]

            # Store for combined plot
            combined_pie_data[step] = (labels, values, colors)

            # Create the pie chart (individual plot)
            fig, ax = plt.subplots(figsize=(10, 8))
            wedges, texts, autotexts = ax.pie(
                values,
                labels=None,
                colors=colors,
                autopct='%1.1f%%',
                startangle=140
            )

            ax.legend(
                handles=wedges,
                labels=labels,
                loc='center left',
                bbox_to_anchor=(1, 0.5),
                frameon=False
            )

            # Save individual pie chart
            plt.savefig(f"{output_dir}/{scenario}_resource_contribution_step_{step}.png", bbox_inches='tight', facecolor="white", edgecolor="white")
            plt.close()

            # Reset cumulative data for next step
            cumulative_data = pd.DataFrame()

    # Create combined 2x2 plot
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))

    # To store labels and wedges for the shared legend
    all_labels = []
    all_wedges = []

    for idx, (step, (labels, values, colors)) in enumerate(combined_pie_data.items()):
        row, col = divmod(idx, 2)
        wedges, texts, autotexts = axs[row, col].pie(
            values,
            labels=None,  # No labels on pie chart
            colors=colors,
            autopct='%1.1f%%',
            startangle=140
        )
        axs[row, col].set_title(f"Step {step}", pad=5)

        # Store the first wedge for each label for the legend
        for label, wedge in zip(labels, wedges):
            if label not in all_labels:
                all_labels.append(label)
                all_wedges.append(wedge)

    # Create a single shared legend for the entire figure
    fig.legend(
        handles=all_wedges,
        labels=all_labels,
        loc='lower center',
        ncol=len(all_labels),  # Arrange legends horizontally
        fontsize=12,
        frameon=False
    )

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Leave space for legend and title
    plt.savefig(f"{output_dir}/{scenario}_combined_resource_contribution.png", bbox_inches='tight', facecolor="white", edgecolor="white")
    plt.close()

    print(f'Finished plotting combined pie charts for {scenario}')


