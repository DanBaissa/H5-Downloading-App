from bokeh.io import output_file, show
from bokeh.models import GeoJSONDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.palettes import Viridis6 as palette
from bokeh.models import CategoricalColorMapper
import geopandas as gpd
import json

# Read the shapefile
shapefile = gpd.read_file('Data/Black_Marble_IDs/Black_Marble_World_tiles.shp')

# Convert to GeoJSON
json_data = json.loads(shapefile.to_json())

# Create a DataSource from the GeoJSON
source = GeoJSONDataSource(geojson=json.dumps(json_data))

# Define a color mapper
color_mapper = CategoricalColorMapper(factors=shapefile['TileID'].unique(),
                                      palette=palette)

# Create a figure
p = figure(background_fill_color="lightgray")

# Add the polygons from the GeoJSONDataSource
p.patches('xs', 'ys', source=source,
          fill_color={'field': 'TileID', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.5)

# Add a hover tool
hover = HoverTool(tooltips=[("TileID", "@TileID")])
p.add_tools(hover)

# Display the figure
output_file("shapefile.html")
show(p)
