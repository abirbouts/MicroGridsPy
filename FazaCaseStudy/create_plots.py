import pandas as pd
import matplotlib.pyplot as plt
import os

# Path to the Excel file
file_path = 'FazaCaseStudy\\Energy Balance - Scenario 1.xlsx'

# Load the Excel file with multiple sheets
data = pd.ExcelFile(file_path)

# Output directory for saving plots
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)

# Iterate through each sheet and calculate averages for every hour of the day
all_years_avg = []
i=0
for sheet_name in data.sheet_names:
    # Load the data for the current sheet
    df = data.parse(sheet_name)
    # Delete columns that have 'total production' in the name
    df = df.loc[:, ~df.columns.str.contains('Total Production', case=False)]
    df = df.drop(columns=['Battery State of Charge (%)', 'DC System Feed In Losses (kWh)', 'DC System Charge Losses (kWh)'])

    # Rename columns that have 'Actual Production' in the name to 'Production'
    df.columns = df.columns.str.replace('Actual Production', 'Production', case=False)
    
    # Create a timestamp starting at 01 am on the first of January
    year = 2022 + i
    i+=1
    start_time = f'{year}-01-01 00:00:00'
    end_time = f'{year}-12-31 23:00:00'
    date_range = pd.date_range(start=start_time, end=end_time, freq='h')
    date_range = date_range[~((date_range.month == 2) & (date_range.day == 29))]
    df.index = date_range
    
    # Group by hour and calculate averages
    hourly_avg = df.groupby(df.index.hour).mean()
    hourly_avg['Hour'] = hourly_avg.index
    all_years_avg.append(hourly_avg)
    
    # Plot the data for the current year
    plt.figure(figsize=(10, 6))
    for column in df.columns:
        if column not in ['Hour']:
            plt.plot(hourly_avg.index, hourly_avg[column], label=column)
    plt.title(f"Average Hourly Data for {sheet_name}")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Value")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{output_dir}/average_hourly_{sheet_name}.png")
    plt.close()

# Combine all years into a single dataframe for overall averages
combined_avg = pd.concat(all_years_avg).groupby('Hour').mean()

# Plot the data for all years together
plt.figure(figsize=(10, 6))
for column in combined_avg.columns:
    plt.plot(combined_avg.index, combined_avg[column], label=column)
plt.title("Average Hourly Data for All Years Combined")
plt.xlabel("Hour of Day")
plt.ylabel("Average Value")
plt.legend()
plt.grid(True)
plt.savefig(f"{output_dir}/average_hourly_all_years.png")
plt.close()
