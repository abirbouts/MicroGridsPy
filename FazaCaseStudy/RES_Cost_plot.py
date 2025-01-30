import pandas as pd
import matplotlib.pyplot as plt

# Load NREL data from CSV
resource = 'solar'
initial_price_kenya = 1600  # Initial cost in Kenya (USD/kW or USD/kWh) in the first year of the data
nrel_data = pd.read_csv(f'nrel_{resource}_cost.csv')

initial_price_nrel = nrel_data.iloc[0, 1]  # Initial solar cost in NREL data (first year, first scenario)

# Calculate adjustment factor for Kenya
adjustment_factor = initial_price_kenya / initial_price_nrel

# Adjust NREL data for Kenya
kenya_data = nrel_data.copy()
kenya_data['Conservative'] = kenya_data['Conservative'] * adjustment_factor
kenya_data['Moderate'] = kenya_data['Moderate'] * adjustment_factor
kenya_data['Advanced'] = kenya_data['Advanced'] * adjustment_factor

# Plot results
plt.figure(figsize=(12, 6))
for scenario in ['Conservative', 'Moderate', 'Advanced']:
    plt.plot(kenya_data['Year'], kenya_data[scenario], label=scenario)
if resource == 'solar':
    plt.title('Solar Cost Projections (Kenya)')
if resource == 'battery':
    plt.title('Battery Cost Projections (Kenya)')
if resource == 'wind':
    plt.title('Wind Cost Projections (Kenya)')
plt.xlabel('Year')
if resource == 'battery':
    plt.ylabel('Cost (USD/kWh)')
else:
    plt.ylabel('Cost (USD/kW)')
plt.xticks(ticks=nrel_data['Year'], labels=nrel_data['Year'])  # Ensure x-axis only shows integer years
plt.legend()
plt.grid(True)
plt.show()
