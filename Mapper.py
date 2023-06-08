import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import geopandas as gpd

# Load the shapefile
shapefile = gpd.read_file('Data/Black_Marble_IDs/Black_Marble_World_tiles.shp')


def select_country():
    # Clear the output text box
    output.delete(1.0, tk.END)

    # Get the country selected by the user and remove any leading or trailing whitespaces
    selected_country = country_var.get().strip()

    # Filter the shapefile to get the rows for the selected country
    selected_rows = shapefile[shapefile['COUNTRY'] == selected_country]

    # Get the TileID values for the selected country and convert them to a list
    tile_ids = selected_rows['TileID'].tolist()

    # Save the 'TileID' values to a .txt file (This will overwrite any existing file)
    selected_rows['TileID'].to_csv(selected_country + '_TileIDs.txt', index=False, header=False)

    # Print TileID values to the output text box
    for tile_id in tile_ids:
        output.insert(tk.END, str(tile_id) + '\n')


# Create a new tkinter window
root = tk.Tk()

# Add a dropdown menu (combobox) with all unique values of the 'COUNTRY' column
country_var = tk.StringVar()
country_dropdown = ttk.Combobox(root, textvariable=country_var)
# remove quotation marks from country names and convert the numpy array to a list
country_dropdown['values'] = [str(i) for i in shapefile['COUNTRY'].unique().tolist()]
country_dropdown.pack()

# Add a submit button that will execute the select_country function when clicked
submit_button = ttk.Button(root, text='Submit', command=select_country)
submit_button.pack()

# Add an output text box
output = scrolledtext.ScrolledText(root, width=40, height=10)
output.pack()

# Start the tkinter event loop
root.mainloop()
