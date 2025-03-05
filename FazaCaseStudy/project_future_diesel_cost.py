import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

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

# Define colors to match previous scenario colors
colors = {
    'Historical': '#000000',  # Black for historical data
    '450 Scenario': '#E57373',  # Muted Red for conservative
    'Current Policies': '#64B5F6',  # Steel Blue for moderate
    'New Policies': '#81C784'  # Soft Green for advanced
}

# Diesel Prices in Kenya (Historical Data)
year_historical = [2022, 2023, 2024, 2025]
diesel_price_historical = [141.06, 201.47, 171.6, 165.37]  # Diesel price in KES
exchange_rate_historical = [118.25, 146.95, 130.03, 128.5]  # Exchange rate for each year (KES/USD)

diesel_price_df = pd.DataFrame({'Year': year_historical, 
                                'Diesel Price (KES)': diesel_price_historical, 
                                'Exchange Rate (KES/USD)': exchange_rate_historical})
diesel_price_df['Diesel Price (USD)'] = diesel_price_df['Diesel Price (KES)'] / diesel_price_df['Exchange Rate (KES/USD)']

# Heat Roadmap Oil Price Projections (in EUR/MWh)
years_oil = np.array([2015, 2030, 2050])  # Given years
oil_prices_450 = np.array([30.54, 49.98, 42.04])  # 450 Scenario
oil_prices_current = np.array([30.54, 73.93, 96.66])  # Current Policies Scenario
oil_prices_new = np.array([30.54, 64.81, 79.69])  # New Policies Scenario

# Diesel price in Kenya for 2025 (in USD/liter)
diesel_2025 = diesel_price_df.loc[diesel_price_df['Year'] == 2025, 'Diesel Price (USD)'].values[0]

# Estimate the diesel-to-oil price ratio in 2025 for each scenario
oil_2025_450 = np.interp(2025, years_oil, oil_prices_450)
oil_2025_current = np.interp(2025, years_oil, oil_prices_current)
oil_2025_new = np.interp(2025, years_oil, oil_prices_new)

ratio_450 = diesel_2025 / oil_2025_450
ratio_current = diesel_2025 / oil_2025_current
ratio_new = diesel_2025 / oil_2025_new

# Interpolate oil prices for each scenario
oil_interp_450 = interp1d(years_oil, oil_prices_450, kind='linear', fill_value='extrapolate')
oil_interp_current = interp1d(years_oil, oil_prices_current, kind='linear', fill_value='extrapolate')
oil_interp_new = interp1d(years_oil, oil_prices_new, kind='linear', fill_value='extrapolate')

# Generate future price estimates from 2025 to 2041
years_future = np.arange(2025, 2042)  # Until 2041
oil_future_450 = oil_interp_450(years_future)
oil_future_current = oil_interp_current(years_future)
oil_future_new = oil_interp_new(years_future)

diesel_future_450 = oil_future_450 * ratio_450
diesel_future_current = oil_future_current * ratio_current
diesel_future_new = oil_future_new * ratio_new

# Create DataFrame for historical and projected diesel prices
df_future = pd.DataFrame({
    "Year": years_future,
    "Diesel Price in Kenya (USD/liter) - 450": diesel_future_450,
    "Diesel Price in Kenya (USD/liter) - Current Policies": diesel_future_current,
    "Diesel Price in Kenya (USD/liter) - New Policies": diesel_future_new
})

# Combine historical and future data
df_historical = diesel_price_df[['Year', 'Diesel Price (USD)']]
df_historical = df_historical.rename(columns={"Diesel Price (USD)": "Diesel Price in Kenya (USD/liter) - Historical"})

df_combined = pd.merge(df_historical, df_future, on="Year", how="outer").sort_values("Year")

# Save to CSV
df_combined.to_csv('FazaCaseStudy\\diesel_price_projections.csv', index=False)

# Plot the results
plt.figure(figsize=(12, 6))

# Plot historical data
plt.plot(df_combined["Year"], df_combined["Diesel Price in Kenya (USD/liter) - Historical"], 
         label="Historical Diesel Price", marker='o', linestyle='-', color=colors['Historical'], linewidth=2.5)

# Plot future projections
plt.plot(df_combined["Year"], df_combined["Diesel Price in Kenya (USD/liter) - 450"], 
         label="450 Scenario", marker='o', linestyle='-', color=colors['450 Scenario'], linewidth=2.5)
plt.plot(df_combined["Year"], df_combined["Diesel Price in Kenya (USD/liter) - Current Policies"], 
         label="Current Policies", marker='s', linestyle='--', color=colors['Current Policies'], linewidth=2.5)
plt.plot(df_combined["Year"], df_combined["Diesel Price in Kenya (USD/liter) - New Policies"], 
         label="New Policies", marker='^', linestyle=':', color=colors['New Policies'], linewidth=2.5)

# Set titles and labels
plt.xlabel("Year")
plt.ylabel("Diesel Price (USD/liter)")

# Format x-axis and add legend
plt.xticks(df_combined["Year"].astype(int), rotation=45)
plt.legend(frameon=True, loc='upper left')
plt.grid(True, which='both', linestyle='--', linewidth=0.7, alpha=0.7)

# Save and show the plot
plt.tight_layout()
plt.savefig(f'FazaCaseStudy\\diesel_price.png', bbox_inches='tight', facecolor="white", edgecolor="white")
