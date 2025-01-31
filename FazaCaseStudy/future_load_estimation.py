import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def calculate_connections_per_year():
    # Calculate connected households
    total_households = 605 + 735 + 513 + 381 + 805 + 414 # Sum households in all villages
    total_connected = (3800 / 17540) * total_households # Switching from inhabitants to households (as in thesis it only says how many inhabitants are connected)

    data_first_5_years = [42, 54, 27, 18, 9] # Evolution over first 5 years based on Dynamic Energy Demand Estimation in Rural Mini-Grids paper
    scaling_factor = total_connected / sum(data_first_5_years) # Get scaling factor
    data_first_5_years = [value * scaling_factor for value in data_first_5_years] # Scale data for first five years

    # Calculate the average growth rate from the first 5 years
    growth_rates = []
    for i in range(1, len(data_first_5_years)):
        growth_rate = (data_first_5_years[i] - data_first_5_years[i - 1]) / data_first_5_years[i - 1]
        growth_rates.append(growth_rate)
    average_growth_rate = np.mean(growth_rates)

    # Calculate low, middle, and high growth rates
    high_growth = 0.5 * average_growth_rate
    middle_growth = average_growth_rate
    low_growth = 1.5 * average_growth_rate
    years = np.arange(1, 26)  # From year 1 to year 20
    data_low = [data_first_5_years[-1]]  # Start from the last known value
    data_middle = [data_first_5_years[-1]]
    data_high = [data_first_5_years[-1]]

    # Calculate the evolution for low, middle, and high growth rates
    for year in range(6, 26):
        data_low.append(data_low[-1] * (1 + low_growth))
        data_middle.append(data_middle[-1] * (1 + middle_growth))
        data_high.append(data_high[-1] * (1 + high_growth))

    years += 2016

    # Create dataframe
    table_data = {
        "Year": years,
        "Low Growth": [*data_first_5_years, *data_low[1:]],
        "Middle Growth": [*data_first_5_years, *data_middle[1:]],
        "High Growth": [*data_first_5_years, *data_high[1:]],
    }

    df = pd.DataFrame(table_data)

    # Compute cumulative values for each growth scenario
    df["Cumulative Low Growth"] = df["Low Growth"].cumsum()
    df["Cumulative Middle Growth"] = df["Middle Growth"].cumsum()
    df["Cumulative High Growth"] = df["High Growth"].cumsum()

    # Plot the individual growth graphs
    plt.figure(figsize=(10, 6))
    plt.plot(years, df["Low Growth"], label="Low Growth", linestyle="--")
    plt.plot(years, df["Middle Growth"], label="Middle Growth", linestyle="-")
    plt.plot(years, df["High Growth"], label="High Growth", linestyle=":")

    plt.xlabel("Year")
    plt.ylabel("New Household Connections")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot cumulative growth graphs
    plt.figure(figsize=(10, 6))
    plt.plot(years, df["Cumulative Low Growth"], label="Cumulative Low Growth", linestyle="--")
    plt.plot(years, df["Cumulative Middle Growth"], label="Cumulative Middle Growth", linestyle="-")
    plt.plot(years, df["Cumulative High Growth"], label="Cumulative High Growth", linestyle=":")

    plt.xlabel("Year")
    plt.ylabel("Cumulative Household Connections")
    plt.legend()
    plt.grid(True)
    plt.show()

    return df

def get_average_appliance_tier(df):
    growth_rates = ["Low Growth", "Middle Growth", "High Growth"]
    L_early_adopters = 5
    L_late_adopters = [4, 4.5, 5]
    k_early_adopters = 0.5641
    k_late_adopters = [0.333, 0.319, 0.308]
    x0_early_adopters = 1.5137
    x0_late_adopters = [5.315, 5.963, 6.545]

    for year in range(2017, 2042):
        for i, growth_rate in enumerate(growth_rates):
            appliance_tier_list = []
            connected_households_list = []
            for years_connected in range(0, year - 2016):
                connected_households_this_year = df.loc[df["Year"] == year - years_connected, growth_rate].values[0]
                connected_households_list.append(connected_households_this_year)
                appliance_tier_early_adopters = L_early_adopters / (1 + np.exp(-k_early_adopters * (years_connected - x0_early_adopters)))
                appliance_tier_late_adopters = L_late_adopters[i] / (1 + np.exp(-k_late_adopters[i] * (years_connected - x0_late_adopters[i])))
                appliance_tier_list.append(0.3 * appliance_tier_early_adopters + 0.7 * appliance_tier_late_adopters)
                
            average_appliance_tier = np.dot(appliance_tier_list, connected_households_list) / sum(connected_households_list)
            df.loc[df["Year"] == year, f"Average Appliance Tier {growth_rate}"] = average_appliance_tier
    
    return df

def get_demand_increase(initial_demand, df):
    low_growth_demand_df = pd.DataFrame()
    middle_growth_demand_df = pd.DataFrame()
    high_growth_demand_df = pd.DataFrame()

    for growth_rate in ["Low Growth", "Middle Growth", "High Growth"]:
        for year in range(2022, 2042):
            if year == 2022:
                cummulated_demand_increase = 1
                df.loc[df["Year"] == year, f"Average Demand Increase {growth_rate}"] = cummulated_demand_increase
            else:
                connected_households = df.loc[df["Year"] == year, f'Cumulative {growth_rate}'].values[0]
                connected_households_prev = df.loc[df["Year"] == year - 1, f'Cumulative {growth_rate}'].values[0]
                average_appliance_tier = df.loc[df["Year"] == year, f"Average Appliance Tier {growth_rate}"].values[0]
                average_appliance_tier_prev = df.loc[df["Year"] == year - 1, f"Average Appliance Tier {growth_rate}"].values[0]
                demand_increase =  (1 + 0.45*(average_appliance_tier-average_appliance_tier_prev)) * (connected_households / connected_households_prev)
                df.loc[df["Year"] == year, f"Average Demand Increase {growth_rate}"] = demand_increase
                cummulated_demand_increase *= demand_increase
            if growth_rate == "Low Growth":
                low_growth_demand_df[str(year)] = initial_demand["2022"] * cummulated_demand_increase
            elif growth_rate == "Middle Growth":
                middle_growth_demand_df[str(year)] = initial_demand["2022"] * cummulated_demand_increase
            else:
                high_growth_demand_df[str(year)] = initial_demand["2022"] * cummulated_demand_increase
    
    # Plot average demand increase
    plt.figure(figsize=(10, 6))
    for growth_rate in ["Low Growth", "Middle Growth", "High Growth"]:
        plt.plot(df["Year"], df[f"Average Demand Increase {growth_rate}"], label=f"Average Demand Increase {growth_rate}")

    plt.xlabel("Year")
    plt.ylabel("Average Demand Increase")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot cumulative demand increase
    plt.figure(figsize=(10, 6))
    for growth_rate in ["Low Growth", "Middle Growth", "High Growth"]:
        cumulative_demand_increase = df[f"Average Demand Increase {growth_rate}"].cumprod()
        plt.plot(df["Year"], cumulative_demand_increase, label=f"Cumulative Demand Increase {growth_rate}")

    plt.xlabel("Year")
    plt.ylabel("Cumulative Demand Increase")
    plt.legend()
    plt.grid(True)
    plt.show()

    return low_growth_demand_df, middle_growth_demand_df, high_growth_demand_df


df = calculate_connections_per_year()

df = get_average_appliance_tier(df)

# Extract column 1 and 2 from sheet "Whole year" without loading the whole xlsx
initial_year_data_30min = pd.read_excel("FazaCaseStudy\Total 2022.xlsx", sheet_name="Whole year", usecols=[2])
initial_year_data_30min.rename(columns={"METER READING [kWh]": "2022"}, inplace=True)
initial_year_data_30min["2022"] = initial_year_data_30min["2022"] * 1000

# Create a new DataFrame with half the length by summing pairs of rows
initial_year_data = initial_year_data_30min.groupby(initial_year_data_30min.index // 2).sum()

low_growth_demand_df, middle_growth_demand_df, high_growth_demand_df = get_demand_increase(initial_year_data, df)

low_growth_demand_df.to_csv("FazaCaseStudy\low_growth_demand.csv", index=False)
middle_growth_demand_df.to_csv("FazaCaseStudy\middle_growth_demand.csv", index=False)
high_growth_demand_df.to_csv("FazaCaseStudy\high_growth_demand.csv", index=False)