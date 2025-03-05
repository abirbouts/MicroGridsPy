import pandas as pd
import matplotlib.pyplot as plt


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

# Function to plot wind energy comparison
def plot_wind_energy_comparison(csv_file1, csv_file2):
    # Load data
    df_nasa = pd.read_csv(csv_file1)
    df_pvgis = pd.read_csv(csv_file2)

    # Assuming periods start at 1 AM on January 1st
    df_nasa['Day'] = ((df_nasa['Periods'] - 1) // 24) + 1
    df_pvgis['Day'] = ((df_pvgis['Periods'] - 1) // 24) + 1

    # Calculate hourly statistics for wind energy
    hourly_stats_nasa = df_nasa.groupby(df_nasa['Periods'] % 24)['Wind'].agg(['mean', 'min', 'max'])
    hourly_stats_pvgis = df_pvgis.groupby(df_pvgis['Periods'] % 24)['Wind'].agg(['mean', 'min', 'max'])

    # Calculate total average wind energy
    avg_wind_nasa = df_nasa['Wind'].mean()
    avg_wind_pvgis = df_pvgis['Wind'].mean()

    # Plot daily pattern
    fig, ax = plt.subplots(figsize=(12, 6))
    hours = hourly_stats_nasa.index
    ax.plot(hours, hourly_stats_nasa['mean'], label='NASA Output', color='#E57373')
    ax.plot(hours, hourly_stats_pvgis['mean'], label='PVGIS Output', color='#64B5F6')
    ax.fill_between(hours, hourly_stats_nasa['min'], hourly_stats_nasa['max'], color='#E57373', alpha=0.3, label='NASA Output Range')
    ax.fill_between(hours, hourly_stats_pvgis['min'], hourly_stats_pvgis['max'], color='#64B5F6', alpha=0.3, label='PVGIS Output Range')
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Wind Energy Production [Wh]')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # Add total average wind energy to the plot
    ax.grid(True)
    plt.tight_layout()

    # Show plot
    plt.savefig("FazaCaseStudy/plots/wind_nasa_vs_pvgis.png", bbox_inches='tight', facecolor="white", edgecolor="white")

# Example usage
if __name__ == '__main__':
    csv_file1 = 'FazaCaseStudy/Resources Availability Nasa.csv'
    csv_file2 = 'FazaCaseStudy/Resources Availability PVGIS.csv'
    plot_wind_energy_comparison(csv_file1, csv_file2)
