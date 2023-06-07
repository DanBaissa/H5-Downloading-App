import geopandas as gpd
import folium
from folium.plugins import MarkerCluster

# Load the shapefile
gdf = gpd.read_file('Data/Black_Marble_IDs/Black_Marble_World_tiles.shp')

# Reproject to a projected CRS (example uses EPSG:3857, Web Mercator)
gdf = gdf.to_crs('EPSG:3857')

# Create a folium map
m = folium.Map([gdf['geometry'].centroid.y.mean(),
                gdf['geometry'].centroid.x.mean()],
                zoom_start=10)

# Function to add a clickable marker for each shape
def add_marker(row):
    marker = folium.Marker(location=[row['geometry'].centroid.y,
                                     row['geometry'].centroid.x])
    # Convert the attributes to a string instead of trying to use to_json
    popup = folium.Popup(f"{row}", max_width=500)
    marker.add_child(popup)
    marker.add_to(m)

# Apply function
gdf.apply(add_marker, axis=1)

# Display map
m
