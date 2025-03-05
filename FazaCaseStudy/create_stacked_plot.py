import pandas as pd
import matplotlib.pyplot as plt
import os

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

# Path to the Excel file
file_path = 'FazaCaseStudy//Energy Balance - Scenario 1.xlsx'

# Load the Excel file with multiple sheets
data = pd.ExcelFile(file_path)

# Output directory for saving plots
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)

# Iterate through each sheet and calculate averages for every hour of the day
all_years_avg = []
i = 0
for sheet_name in data.sheet_names:
    if i >= 3:
        break
    df = data.parse(sheet_name)
    df = df.loc[:, ~df.columns.str.contains('Total Production', case=False)]
    df = df.drop(columns=['Battery State of Charge (%)', 'DC System Feed In Losses (kWh)', 'DC System Charge Losses (kWh)'], errors='ignore')
    df.columns = df.columns.str.replace('Actual Production', 'Production', case=False)
    
    year = 2022 + i
    print(year)
    i += 1
    start_time = f'{year}-01-01 00:00:00'
    end_time = f'{year}-12-31 23:00:00'
    date_range = pd.date_range(start=start_time, end=end_time, freq='h')
    date_range = date_range[~((date_range.month == 2) & (date_range.day == 29))]
    df.index = date_range
    
    hourly_avg = df.groupby(df.index.hour).mean()
    hourly_avg['Hour'] = hourly_avg.index
    all_years_avg.append(hourly_avg)

# Combine all years into a single dataframe for overall averages
combined_avg = pd.concat(all_years_avg).groupby('Hour').mean()

# Drop 'Solar PV Transformation Losses (kWh)' if 'DC System Transformation Losses (kWh)' exists
if 'DC System Transformation Losses (kWh)' in combined_avg.columns:
    combined_avg = combined_avg.drop(columns=['Solar PV Transformation Losses (kWh)'], errors='ignore')

# Define color mapping
production_colors = {
    'Solar PV Production (kWh)': '#FFC107',
    'Wind Production (kWh)': '#03A9F4',
    'Diesel Generator Production (kWh)': '#8B4513',
    'Battery Outflow (kWh)': '#4CAF50'
    }
demand_color = '#000000'

DEFAULT_COLORS = {
    'Demand': '#000000',  # Black
    'Curtailment': '#E53935',  # Orange
    'Battery': '#4CAF50',  # Light Blue
    'Electricity Purchased': '#800080',  # Purple
    'Electricity Sold': '#008000',  # Green
    'Lost Load': '#F21B3F',  # Red
    'Solar PV': '#FFC107',
    'Wind': "#03A9F4",
    'Diesel Generator': '#8B4513',
    "Fuel": '#8B4513',
    "Fixed O&M": "#FF9800",
    "Variable": "#FF9800",
    "Investment": "#1976D2"
}

# Define transformation loss and curtailment patterns
loss_pattern = {'hatch': '//', 'color': 'red', 'linewidth': 0.5}
curtailment_pattern = {'hatch': '//', 'color': 'grey', 'linewidth': 0.5}

# Prepare data for plotting
fig, ax = plt.subplots(figsize=(12, 7))

# Stack all production values
bottom_stack = pd.Series(0, index=combined_avg.index)
for column in production_colors.keys():
    if column in combined_avg.columns:
        ax.bar(combined_avg.index, combined_avg[column], bottom=bottom_stack, color=production_colors[column], label=column)
        bottom_stack += combined_avg[column]

# Add transformation losses as striped bars
negative_stack = pd.Series(0, index=combined_avg.index)
# Battery inflow should be plotted as negative values
if 'Battery Inflow (kWh)' in combined_avg.columns:
    ax.bar(combined_avg.index, -combined_avg['Battery Inflow (kWh)'], bottom=negative_stack, color=production_colors['Battery Outflow (kWh)'], label='Battery Inflow (kWh)')
    negative_stack -= combined_avg['Battery Inflow (kWh)']

# Add curtailment as grey-striped bars
for prod_col in production_colors.keys():
    curtail_col = prod_col.replace("Production", "Curtailment")
    if curtail_col in combined_avg.columns:
        if 'Curtailment' in curtail_col:
            ax.bar(combined_avg.index, combined_avg[curtail_col], bottom=bottom_stack, color=production_colors[prod_col], edgecolor=curtailment_pattern['color'], hatch=curtailment_pattern['hatch'], label=curtail_col)
            bottom_stack -= combined_avg[curtail_col]

for prod_col in production_colors.keys():
    loss_col = prod_col.replace("Production", "Transformation Losses")
    if loss_col in combined_avg.columns:
        if 'Transformation Losses' in loss_col:
            ax.bar(combined_avg.index, -combined_avg[loss_col], bottom=negative_stack, color=production_colors[prod_col], edgecolor=loss_pattern['color'], hatch=loss_pattern['hatch'], label=loss_col)
            negative_stack -= combined_avg[loss_col]
if 'DC System Transformation Losses (kWh)' in combined_avg.columns:
    ax.bar(combined_avg.index, -combined_avg['DC System Transformation Losses (kWh)'], bottom=negative_stack, color=production_colors['Battery Outflow (kWh)'], edgecolor=loss_pattern['color'], hatch=loss_pattern['hatch'], label='DC System Transformation Losses (kWh)')
    negative_stack -= combined_avg['DC System Transformation Losses (kWh)']

# Plot demand as a line plot
if 'Demand (kWh)' in combined_avg.columns:
    ax.plot(combined_avg.index, combined_avg['Demand (kWh)'], color=demand_color, label='Demand (kWh)', linewidth=2)

# Labels and legend
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Energy (kWh)")
ax.set_title("Average Hourly Energy Balance")
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
ax.grid(True)

# Save and show the plot
plt.savefig(f"{output_dir}/stacked_energy_balance.png", bbox_inches='tight', facecolor="white", edgecolor="white")
plt.show()
