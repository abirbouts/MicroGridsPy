import geopandas as gpd
import matplotlib.pyplot as plt
textwidthfraction = 0.6
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
    "ytick.labelsize": fontsize2,
    "hatch.linewidth": 3.0
})

# Load world dataset
world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")

# Select Kenya for the main map
kenya = world[world["ADMIN"] == "Kenya"]

# Define Faza, Kenya coordinates
faza_coords = {"lat": -2.06, "lon": 41.11}

# Create a figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot only Kenya in the main map without coloring it
kenya.plot(ax=ax, color="none", edgecolor="black", label="Kenya")

# Mark Faza with a black location arrow
ax.scatter(faza_coords["lon"], faza_coords["lat"], color='#E57373', s=100, marker="x", label="Faza, Kenya")

# Add country label
ax.text(37.5, 0.5, "Kenya", fontweight="bold", ha="center", color="black")

# Add title and legend
ax.legend()

# Add an inset map showing Africa
ax_inset = fig.add_axes([0, 0.48, 0.4, 0.4])  # (left, bottom, width, height)
world[world["CONTINENT"] == "Africa"].plot(ax=ax_inset, color="lightgray", edgecolor="black")
kenya.plot(ax=ax_inset, color='#E57373', alpha=0.6, edgecolor="black")  # Highlight Kenya in red

# Remove axis labels from both maps
ax.set_xticks([])
ax.set_yticks([])
ax_inset.set_xticks([])
ax_inset.set_yticks([])

# Save and show the map
plt.savefig("FazaCaseStudy\\faza_location_kenya_only.png", dpi=300, bbox_inches="tight")
plt.show()