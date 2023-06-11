import os
import re
import h5py
import rasterio
import geopandas as gpd
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from rasterio.transform import from_bounds

# Load the shapefile
shapefile = gpd.read_file('Data/Black_Marble_IDs/Black_Marble_World_tiles.shp')

def select_folder_and_save_files():
    # Clear the output text box
    output.delete(1.0, tk.END)

    # Get the country selected by the user and remove any leading or trailing whitespaces
    selected_country = country_var.get().strip()

    # Filter the shapefile to get the rows for the selected country
    selected_rows = shapefile[shapefile['COUNTRY'] == selected_country]

    # Let the user select the directory
    folder_selected = filedialog.askdirectory()

    # Get a list of all .h5 files in the selected directory
    files = [f for f in os.listdir(folder_selected) if f.endswith('.h5')]

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

                # Write the raster data as a GeoTIFF
                with rasterio.open(
                    f"output_{tile_id}.tif",
                    "w",
                    driver="GTiff",
                    height=gap_filled_dnb_brdf_corrected_ntl.shape[0],
                    width=gap_filled_dnb_brdf_corrected_ntl.shape[1],
                    count=1,
                    dtype=gap_filled_dnb_brdf_corrected_ntl.dtype,
                    crs=shape.crs.to_epsg(),  # Use the CRS of the shapefile
                    transform=from_bounds(left, bottom, right, top, gap_filled_dnb_brdf_corrected_ntl.shape[1], gap_filled_dnb_brdf_corrected_ntl.shape[0]),  # Generate the transform from the shape bounds
                ) as dest:
                    dest.write(gap_filled_dnb_brdf_corrected_ntl, 1)
            output.insert(tk.END, f"Finished processing {file}\n")

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
