import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

resource = "Solar PV"

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
    df['Day'] = ((df[period_col] - 1) // 24) + 1
    return df

# Function to convert day number to date (without year)
def day_to_date(day_num):
    base_date = datetime.datetime(2001, 1, 1)  # Using a non-leap year
    target_date = base_date + datetime.timedelta(days=int(day_num) - 1)  # Convert to int
    return target_date.strftime('%d %b')


if __name__ == '__main__':
    csv_file1 = 'FazaCaseStudy\\Resources Availability Nasa.csv'
    csv_file2 = 'FazaCaseStudy\\Resources Availability PVGIS.csv'

    # Get data for both datasets
    df_nasa = get_daily_energy(csv_file1)
    df_pvgis = get_daily_energy(csv_file2)

    # Find the worst and best day for both datasets
    worst_day_nasa_num = ((df_nasa.groupby('Day')[resource].sum()).idxmin())
    best_day_nasa_num = ((df_nasa.groupby('Day')[resource].sum()).idxmax())

    worst_day_pvgis_num = ((df_pvgis.groupby('Day')[resource].sum()).idxmin())
    best_day_pvgis_num = ((df_pvgis.groupby('Day')[resource].sum()).idxmax())

    # Convert day numbers to dates
    worst_day_nasa_date = day_to_date(worst_day_nasa_num)
    best_day_nasa_date = day_to_date(best_day_nasa_num)

    worst_day_pvgis_date = day_to_date(worst_day_pvgis_num)
    best_day_pvgis_date = day_to_date(best_day_pvgis_num)

    # Filter data for the worst and best days
    worst_day_nasa = df_nasa[df_nasa['Day'] == worst_day_nasa_num]
    best_day_nasa = df_nasa[df_nasa['Day'] == best_day_nasa_num]

    worst_day_pvgis = df_pvgis[df_pvgis['Day'] == worst_day_pvgis_num]
    best_day_pvgis = df_pvgis[df_pvgis['Day'] == best_day_pvgis_num]

    # Calculate total energy output for worst and best days
    total_energy_nasa_worst = worst_day_nasa[resource].sum()
    total_energy_nasa_best = best_day_nasa[resource].sum()

    total_energy_pvgis_worst = worst_day_pvgis[resource].sum()
    total_energy_pvgis_best = best_day_pvgis[resource].sum()

    # Correct hour calculation to avoid 0 for 24th hour
    for df in [worst_day_nasa, best_day_nasa, worst_day_pvgis, best_day_pvgis]:
        df['Hour'] = ((df['Periods'] - 1) % 24) + 1

    # Plotting worst days (hourly data)
    plt.figure(figsize=(12, 6))
    plt.plot(worst_day_nasa['Hour'], worst_day_nasa[resource], label=f'NASA {worst_day_nasa_date}', color='#E57373', marker='o')
    plt.plot(worst_day_pvgis['Hour'], worst_day_pvgis[resource], label=f'PVGIS {worst_day_pvgis_date}', color='#64B5F6', marker='o')
    plt.xlabel('Hour of the Day')
    plt.ylabel(f'{resource} Energy (Wh)')
    plt.title(f'Hourly {resource} Energy Production on Worst Day')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Add total energy output as text in the plot
    plt.text(0.05, 0.95, f'NASA Total Energy: {total_energy_nasa_worst:.2f} Wh', transform=plt.gca().transAxes, fontsize=10, color='#E57373', verticalalignment='top')
    plt.text(0.05, 0.90, f'PVGIS Total Energy: {total_energy_pvgis_worst:.2f} Wh', transform=plt.gca().transAxes, fontsize=10, color='#64B5F6', verticalalignment='top')

    plt.grid(True)
    plt.tight_layout()
    output_dir = f'FazaCaseStudy//plots'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig("FazaCaseStudy/plots/solarpv_nasa_vs_pvgis.png", bbox_inches='tight', facecolor="white", edgecolor="white")
    plt.show()

    # Plotting best days (hourly data)
    plt.figure(figsize=(12, 6))
    plt.plot(best_day_nasa['Hour'], best_day_nasa[resource], label=f'NASA {best_day_nasa_date}', color='#E57373', marker='o')
    plt.plot(best_day_pvgis['Hour'], best_day_pvgis[resource], label=f'PVGIS {best_day_pvgis_date}', color='#64B5F6', marker='o')
    plt.xlabel('Hour of the Day')
    plt.ylabel(f'{resource} Energy (Wh)')
    plt.title(f'Hourly {resource} Energy Production on Best Day')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Add total energy output as text in the plot
    plt.text(0.05, 0.95, f'NASA Total Energy: {total_energy_nasa_best:.2f} Wh', transform=plt.gca().transAxes, fontsize=10, color='#E57373', verticalalignment='top')
    plt.text(0.05, 0.90, f'PVGIS Total Energy: {total_energy_pvgis_best:.2f} Wh', transform=plt.gca().transAxes, fontsize=10, color='#64B5F6', verticalalignment='top')

    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plotting total daily energy production
    daily_energy_nasa = df_nasa.groupby('Day')[resource].sum().reset_index()
    daily_energy_pvgis = df_pvgis.groupby('Day')[resource].sum().reset_index()

    avg_daily_nasa = daily_energy_nasa[resource].mean()
    avg_daily_pvgis = daily_energy_pvgis[resource].mean()

    plt.figure(figsize=(12, 6))
    plt.plot(daily_energy_nasa['Day'], daily_energy_nasa[resource], label='NASA Total Daily Energy', color='#E57373')
    plt.plot(daily_energy_pvgis['Day'], daily_energy_pvgis[resource], label='PVGIS Total Daily Energy', color='#64B5F6')
    plt.xlabel('Day of the Year')
    plt.ylabel(f'Total {resource} Energy (Wh)')
    plt.title(f'Total Daily {resource} Energy Production')
    plt.legend()
    plt.text(0.05, 0.05, f'NASA Avg Daily Energy: {avg_daily_nasa:.2f} Wh', transform=plt.gca().transAxes, fontsize=10, color='#E57373', verticalalignment='bottom')
    plt.text(0.05, 0.10, f'PVGIS Avg Daily Energy: {avg_daily_pvgis:.2f} Wh', transform=plt.gca().transAxes, fontsize=10, color='#64B5F6', verticalalignment='bottom')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Print worst and best days with total energy output
    print(f"NASA Worst Day: {worst_day_nasa_date}, Total Energy: {total_energy_nasa_worst:.2f} Wh")
    print(f"PVGIS Worst Day: {worst_day_pvgis_date}, Total Energy: {total_energy_pvgis_worst:.2f} Wh")
    print(f"NASA Best Day: {best_day_nasa_date}, Total Energy: {total_energy_nasa_best:.2f} Wh")
    print(f"PVGIS Best Day: {best_day_pvgis_date}, Total Energy: {total_energy_pvgis_best:.2f} Wh")
