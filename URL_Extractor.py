from datetime import datetime
import re
import tkinter as tk
from tkinter import messagebox


# Function to convert a date string into a Julian date
def date_to_julian(date_string):
    date = datetime.strptime(date_string, "%B %d, %Y")
    julian_date = date.strftime('%Y%j')
    return julian_date


# Function to search for URLs that match a specified date and a list of tiles
def search_urls_by_date_and_tiles(date_string, tiles):
    url_file = "data/URLs.txt"
    date = date_to_julian(date_string)
    search_string = "A" + date
    matching_urls = []

    with open(url_file, 'r') as f:
        for line in f:
            if search_string in line and any(tile in line for tile in tiles):
                matching_urls.append(line.strip())

    return matching_urls


# Function to search for URLs that match a date range and a list of tiles
def search_urls_by_date_range_and_tiles(start_date_string, end_date_string, tiles):
    url_file = "data/URLs.txt"
    start_date = int(date_to_julian(start_date_string))
    end_date = int(date_to_julian(end_date_string))
    matching_urls = []

    with open(url_file, 'r') as f:
        for line in f:
            date_match = re.search("\\d{4}\\d{3}", line)
            if date_match and any(tile in line for tile in tiles):
                julian_date = int(date_match.group(0))
                if start_date <= julian_date <= end_date:
                    matching_urls.append(line.strip())

    return matching_urls


# Function to handle the button click in the GUI
def button_click():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    tiles = [tile.strip() for tile in tile_entry.get().split(',')]
    urls = search_urls_by_date_range_and_tiles(start_date, end_date, tiles)
    # Save the results to a file
    with open('temp.txt', 'w') as f:
        for url in urls:
            f.write("%s\n" % url)
    messagebox.showinfo("Results", "Results saved to temp.txt")


# Create the main window
window = tk.Tk()

# Create and grid the label, entry box, and button for the start date
start_date_label = tk.Label(window, text="Start Date (e.g., 'June 1, 2022'):")
start_date_entry = tk.Entry(window)
start_date_label.grid(row=0, column=0)
start_date_entry.grid(row=0, column=1)

# Create and grid the label, entry box, and button for the end date
end_date_label = tk.Label(window, text="End Date (e.g., 'June 2, 2022'):")
end_date_entry = tk.Entry(window)
end_date_label.grid(row=1, column=0)
end_date_entry.grid(row=1, column=1)

# Create and grid the label, entry box, and button for the tile
tile_label = tk.Label(window, text="Tiles (comma separated, e.g., 'h16v08,h16v09'):")
tile_entry = tk.Entry(window)
tile_label.grid(row=2, column=0)
tile_entry.grid(row=2, column=1)

# Create and grid the submit button
submit_button = tk.Button(window, text="Submit", command=button_click)
submit_button.grid(row=3, column=1)

# Start the main loop
window.mainloop()
