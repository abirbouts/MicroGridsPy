import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point, box
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

# Define Faza, Kenya coordinates
faza_coords = {"lat": -2.056178, "lon": 41.111521}

# Create bounding box with specified distances
north = faza_coords["lat"] + 0.015  # ~1 km north
south = faza_coords["lat"] - 0.16  # ~6 km south
west = faza_coords["lon"] - 0.175  # ~10 km west
east = faza_coords["lon"] + 0.055  # ~1 km east

# Create a bounding box geometry
bounding_box = gpd.GeoDataFrame(
    geometry=[box(west, south, east, north)], crs="EPSG:4326"
)

# Convert to Web Mercator for plotting
bounding_box = bounding_box.to_crs(epsg=3857)

# Create a GeoDataFrame for Faza's location
faza_point = gpd.GeoDataFrame(
    geometry=[Point(faza_coords["lon"], faza_coords["lat"])],
    crs="EPSG:4326"
).to_crs(epsg=3857)

# Create a figure
fig, ax = plt.subplots(figsize=(8, 8))

# Plot the bounding box area
bounding_box.plot(ax=ax, facecolor='none', edgecolor='red', linewidth=0, label='Map Extent')

# Plot the exact location of Faza
faza_point.plot(ax=ax, color='#E57373', markersize=100, marker='x', label='Faza, Kenya')

# Add satellite imagery
ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery)

# Remove axis labels
ax.set_xticks([])
ax.set_yticks([])
ax.legend()

# Save and show the map
plt.savefig("FazaCaseStudy\\faza_satellite_area.png", dpi=300, bbox_inches="tight")
plt.show()