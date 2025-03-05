import pandas as pd
import matplotlib.pyplot as plt
import datetime

resource = "Wind"

# Apply FiveThirtyEight style
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
    "ytick.labelsize": fontsize2
})

# Function to find daily energy totals
def get_daily_energy(csv_file, period_col='Periods', energy_col=resource):
    df = pd.read_csv(csv_file)
    df['Day'] = ((df[period_col] - 1) // 24) + 1  # Convert periods to days
    return df

# Function to convert day number to date (without year)
def day_to_date(day_num):
    base_date = datetime.datetime(2001, 1, 1)  # Using a non-leap year
    target_date = base_date + datetime.timedelta(days=int(day_num) - 1)
    return target_date.strftime('%d %b')

# Example usage
if __name__ == '__main__':
    csv_file1 = 'FazaCaseStudy\\Resources Availability Nasa.csv'
    csv_file2 = 'FazaCaseStudy\\Resources Availability PVGIS.csv'

    # Get data for both datasets
    df_nasa = get_daily_energy(csv_file1)
    df_pvgis = get_daily_energy(csv_file2)

    # Compute total daily resource energy
    daily_energy_nasa = df_nasa.groupby('Day')[resource].sum().reset_index()
    daily_energy_pvgis = df_pvgis.groupby('Day')[resource].sum().reset_index()

    # Compute standard deviation of daily energy
    std_dev_nasa = daily_energy_nasa[resource].std()
    std_dev_pvgis = daily_energy_pvgis[resource].std()

    # Compute mean daily energy
    avg_daily_nasa = daily_energy_nasa[resource].mean()
    avg_daily_pvgis = daily_energy_pvgis[resource].mean()

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot total daily energy production
    ax.plot(daily_energy_nasa['Day'], daily_energy_nasa[resource], label='NASA Total Daily Energy', color='#E57373')
    ax.plot(daily_energy_pvgis['Day'], daily_energy_pvgis[resource], label='PVGIS Total Daily Energy', color='#64B5F6')
    ax.set_xlabel('Day of the Year')
    ax.set_ylabel(f'Total {resource} Energy (Wh)')
    ax.legend()

    # Adjust figure layout to make space on the right for text
    plt.subplots_adjust(right=0.75)  # Shrink plot area to leave space

    # Add text next to the plot
    plt.figtext(0.75, 0.7, f'NASA Avg: {avg_daily_nasa:.2f} Wh', ha='left')
    plt.figtext(0.75, 0.65, f'NASA Std Dev: {std_dev_nasa:.2f} Wh', ha='left')
    plt.figtext(0.75, 0.55, f'PVGIS Avg: {avg_daily_pvgis:.2f} Wh', ha='left')
    plt.figtext(0.75, 0.50, f'PVGIS Std Dev: {std_dev_pvgis:.2f} Wh', ha='left')

    plt.grid(True)
    #plt.tight_layout()
    plt.show()

    # Print standard deviation values
    print(f"NASA Std Dev of Daily {resource} Energy: {std_dev_nasa:.2f} Wh")
    print(f"PVGIS Std Dev of Daily {resource} Energy: {std_dev_pvgis:.2f} Wh")
