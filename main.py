import os
import re
import ssl
import sys
import shutil
import threading
from datetime import datetime
from tkinter import Tk, Button, Label, Entry, StringVar, filedialog, messagebox
from tkinter.ttk import Progressbar
from urllib.request import urlopen, Request

USERAGENT = 'tis/download.py_1.0--' + sys.version.replace('\n','').replace('\r','')

class URLSearcher(Tk):
    def __init__(self):
        super().__init__()

        self.title("URL Search")

        self.start_date = StringVar()
        self.end_date = StringVar()
        self.tiles = StringVar()

        Label(self, text="Start Date (e.g., 'June 1, 2022'):").grid(row=0, column=0)
        Entry(self, textvariable=self.start_date).grid(row=0, column=1)

        Label(self, text="End Date (e.g., 'June 2, 2022'):").grid(row=1, column=0)
        Entry(self, textvariable=self.end_date).grid(row=1, column=1)

        Label(self, text="Tiles (comma separated, e.g., 'h16v08,h16v09'):").grid(row=2, column=0)
        Entry(self, textvariable=self.tiles).grid(row=2, column=1)

        Button(self, text="Submit", command=self.search).grid(row=3, column=0, columnspan=2)

    def search(self):
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        tiles = [tile.strip() for tile in self.tiles.get().split(',')]
        urls = self.search_urls_by_date_range_and_tiles(start_date, end_date, tiles)

        messagebox.showinfo("Results", "URLs are ready for download.")
        self.destroy()

        app = Downloader(urls)
        app.mainloop()

    def date_to_julian(self, date_string):
        date = datetime.strptime(date_string, "%B %d, %Y")
        julian_date = date.strftime('%Y%j')
        return julian_date

    def search_urls_by_date_and_tiles(self, date_string, tiles):
        url_file = "data/URLs.txt"
        date = self.date_to_julian(date_string)
        search_string = "A" + date
        matching_urls = []

        with open(url_file, 'r') as f:
            for line in f:
                if search_string in line and any(tile in line for tile in tiles):
                    matching_urls.append(line.strip())

        return matching_urls

    def search_urls_by_date_range_and_tiles(self, start_date_string, end_date_string, tiles):
        url_file = "data/URLs.txt"
        start_date = int(self.date_to_julian(start_date_string))
        end_date = int(self.date_to_julian(end_date_string))
        matching_urls = []

        with open(url_file, 'r') as f:
            for line in f:
                date_match = re.search("\\d{4}\\d{3}", line)
                if date_match and any(tile in line for tile in tiles):
                    julian_date = int(date_match.group(0))
                    if start_date <= julian_date <= end_date:
                        matching_urls.append(line.strip())

        return matching_urls


class Downloader(Tk):
    def __init__(self, urls):
        super().__init__()

        self.urls = urls
        self.title("H5 Downloader")

        self.destination_folder = StringVar()
        self.token = StringVar()

        Label(self, text='Destination folder:').grid(row=0, column=0)
        Entry(self, textvariable=self.destination_folder).grid(row=0, column=1)
        Button(self, text='Browse...', command=self.browse_destination_folder).grid(row=0, column=2)

        Label(self, text='Token:').grid(row=1, column=0)
        Entry(self, textvariable=self.token).grid(row=1, column=1)

        self.progress = Progressbar(self, orient='horizontal', mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=3)

        Button(self, text='Download', command=self.start_download_thread).grid(row=3, column=0, columnspan=3)

    def browse_destination_folder(self):
        self.destination_folder.set(filedialog.askdirectory())

    def start_download_thread(self):
        threading.Thread(target=self.download_files).start()

    def download_files(self):
        self.progress['maximum'] = len(self.urls)
        self.progress['value'] = 0

        CTX = ssl.SSLContext()
        headers = { 'user-agent' : USERAGENT, 'Authorization' : 'Bearer ' + self.token.get() }

        for url in self.urls:
            url = url.strip()
            filename = url.split('/')[-1]
            dest = os.path.join(self.destination_folder.get(), filename)

            try:
                with urlopen(Request(url, headers=headers), context=CTX) as response:
                    with open(dest, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)
                self.progress['value'] += 1
            except Exception as e:
                messagebox.showerror('Download error', f'Failed to download {url} due to {str(e)}')
                break

        messagebox.showinfo('Download complete', 'Download of all files completed.')


if __name__ == "__main__":
    searcher = URLSearcher()
    searcher.mainloop()
