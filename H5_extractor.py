import os
import re
import h5py
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from rasterio.transform import from_bounds

# Load the shapefiles
shapefile = gpd.read_file('Data/Black_Marble_IDs/Black_Marble_World_tiles.shp')
countries_shapefile = gpd.read_file('Data/World_Countries/World_Countries_Generalized.shp')


def select_folder_and_save_files():
    # Clear the output text box
    output.delete(1.0, tk.END)

    # Get the country selected by the user and remove any leading or trailing whitespaces
    selected_country = country_var.get().strip()

    # Filter the shapefile to get the rows for the selected country
    selected_rows = shapefile[shapefile['COUNTRY'] == selected_country]

    # Find the shape for the selected country in the countries_shapefile
    country_shape = countries_shapefile[countries_shapefile['COUNTRY'] == selected_country]
    if country_shape.empty:
        output.insert(tk.END, f"Could not find shape for {selected_country}\n")
        return

    # Convert the country shape to GeoJSON format
    country_geojson = country_shape.geometry.__geo_interface__

    # Let the user select the directory
    folder_selected = filedialog.askdirectory()

    # Get a list of all .h5 files in the selected directory
    files = [f for f in os.listdir(folder_selected) if f.endswith('.h5')]

    # List to store the raster data
    rasters = []

    # Loop through the files and process them if their TileID is in selected_rows
    for file in files:
        tile_id = re.search('h\d{2}v\d{2}', file).group()
        shape = selected_rows[selected_rows['TileID'] == tile_id]

        if not shape.empty:
            output.insert(tk.END, f"Processing {file}...\n")
            with h5py.File(os.path.join(folder_selected, file), "r") as f:
                data_fields = f["/HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields"]
                gap_filled_dnb_brdf_corrected_ntl = data_fields['Gap_Filled_DNB_BRDF-Corrected_NTL'][...]

                # Perform a log transform on the data
                gap_filled_dnb_brdf_corrected_ntl = np.log1p(gap_filled_dnb_brdf_corrected_ntl)

                # Get the bounds of the shape
                left, bottom, right, top = shape.total_bounds

                # Save the raster data to a temporary GeoTIFF file
                temp_file = os.path.join(folder_selected, f"temp_{tile_id}.tif")
                with rasterio.open(
                        temp_file,
                        "w",
                        driver="GTiff",
                        height=gap_filled_dnb_brdf_corrected_ntl.shape[0],
                        width=gap_filled_dnb_brdf_corrected_ntl.shape[1],
                        count=1,
                        dtype=gap_filled_dnb_brdf_corrected_ntl.dtype,
                        crs=shape.crs.to_epsg(),  # Use the CRS of the shapefile
                        transform=from_bounds(left, bottom, right, top, gap_filled_dnb_brdf_corrected_ntl.shape[1],
                                              gap_filled_dnb_brdf_corrected_ntl.shape[0]),
                ) as dest:
                    dest.write(gap_filled_dnb_brdf_corrected_ntl, 1)

                # Open the temporary file with rasterio and add to the list
                src = rasterio.open(temp_file)
                rasters.append(src)

    # Merge all the rasters and write the result to a new GeoTIFF file
    mosaic, out_trans = merge(rasters)
    out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "crs": src.crs
    })

    # Save the mosaic to a temporary GeoTIFF file
    with rasterio.open(f"temp_{selected_country}.tif", 'w', **out_meta) as dest:
        dest.write(mosaic)

    # Open the temporary file with rasterio
    with rasterio.open(f"temp_{selected_country}.tif") as src:
        # Crop the mosaic using the country's geometry
        mosaic_cropped, _ = mask(src, [country_geojson], crop=True)
        out_meta = src.meta.copy()

    # Update the metadata
    out_meta.update({
        "height": mosaic_cropped.shape[1],
        "width": mosaic_cropped.shape[2],
        "transform": out_trans
    })

    # Save the cropped mosaic to a new GeoTIFF file
    with rasterio.open(f"{selected_country}_merged_cropped.tif", 'w', **out_meta) as dest:
        dest.write(mosaic_cropped)

    # Close the raster files and delete the temporary files
    for raster in rasters:
        raster.close()
        os.remove(raster.name)

    os.remove(f"temp_{selected_country}.tif")

    output.insert(tk.END, "Finished processing\n")


# Create a new tkinter window
root = tk.Tk()

# Add a dropdown menu (combobox) with all unique values of the 'COUNTRY' column
country_var = tk.StringVar()
country_dropdown = ttk.Combobox(root, textvariable=country_var)
# remove quotation marks from country names and convert the numpy array to a list
country_dropdown['values'] = [str(i) for i in shapefile['COUNTRY'].unique().tolist()]
country_dropdown.pack()

# Add a submit button that will execute the select_country function when clicked
submit_button = ttk.Button(root, text='Submit', command=select_folder_and_save_files)
submit_button.pack()

# Add an output text box
output = scrolledtext.ScrolledText(root, width=40, height=10)
output.pack()

# Start the tkinter event loop
root.mainloop()
