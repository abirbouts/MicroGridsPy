import pandas as pd
import matplotlib.pyplot as plt

# Set plot style
plt.style.use('fivethirtyeight')
textwidthfraction = 0.45
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

# Define colors for the scenarios
colors = {
    'Conservative': '#E57373',  # Muted Red (Conservative Scenario)
    'Moderate': '#64B5F6',      # Steel Blue (Moderate Scenario)
    'Advanced': '#81C784'       # Soft Green (Advanced Scenario)
}

# Load NREL data from CSV
resource = 'wind'  # Resource type (solar, battery, wind)
initial_price_kenya = 4042  # Initial cost in Kenya (USD/kW or USD/kWh) in the first year of the data
nrel_data = pd.read_csv(f'FazaCaseStudy\\nrel_{resource}_cost.csv')

# Get initial cost in NREL data (first year, first scenario)
initial_price_nrel = nrel_data.iloc[0, 1]  

# Calculate adjustment factor for Kenya
adjustment_factor = initial_price_kenya / initial_price_nrel

# Adjust NREL data for Kenya
kenya_data = nrel_data.copy()
kenya_data['Conservative'] *= adjustment_factor
kenya_data['Moderate'] *= adjustment_factor
kenya_data['Advanced'] *= adjustment_factor

# Save adjusted data to CSV
kenya_data.to_csv(f'FazaCaseStudy\\kenya_{resource}_cost.csv', index=False)

# Plot results
plt.figure(figsize=(12, 6))

# Define line styles and markers
line_styles = {'Conservative': '-', 'Moderate': '--', 'Advanced': ':'}
markers = {'Conservative': 'o', 'Moderate': 's', 'Advanced': '^'}

for scenario in ['Conservative', 'Moderate', 'Advanced']:
    plt.plot(
        kenya_data['Year'], kenya_data[scenario], 
        label=scenario, color=colors[scenario], 
        linestyle=line_styles[scenario], marker=markers[scenario], linewidth=2.5
    )


plt.xlabel('Year')
plt.ylabel('Cost (USD/kWh)' if resource == 'battery' else 'Cost (USD/kW)')

# Format x-axis and add legend
plt.xticks(ticks=nrel_data['Year'], labels=nrel_data['Year'], rotation=45)
plt.legend(frameon=True, loc='upper right')
plt.grid(True, which='both', linestyle='--', linewidth=0.7, alpha=0.7)

# Save and show plot
plt.tight_layout()
plt.savefig(f'FazaCaseStudy\\{resource}_cost.png', bbox_inches='tight', facecolor="white", edgecolor="white")

