#!/usr/bin/env python
import os
import ssl
import sys
import shutil
from urllib.request import urlopen, Request
from tkinter import Tk, Button, Label, Entry, StringVar, filedialog, messagebox
from tkinter.ttk import Progressbar
import threading

USERAGENT = 'tis/download.py_1.0--' + sys.version.replace('\n','').replace('\r','')

class Downloader(Tk):
    def __init__(self):
        super().__init__()

        self.title("H5 Downloader")

        self.url_file = StringVar()
        self.destination_folder = StringVar()
        self.token = StringVar()

        Label(self, text='URL file:').grid(row=0, column=0)
        Entry(self, textvariable=self.url_file).grid(row=0, column=1)
        Button(self, text='Browse...', command=self.browse_url_file).grid(row=0, column=2)

        Label(self, text='Destination folder:').grid(row=1, column=0)
        Entry(self, textvariable=self.destination_folder).grid(row=1, column=1)
        Button(self, text='Browse...', command=self.browse_destination_folder).grid(row=1, column=2)

        Label(self, text='Token:').grid(row=2, column=0)
        Entry(self, textvariable=self.token).grid(row=2, column=1)

        self.progress = Progressbar(self, orient='horizontal', mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=3)

        Button(self, text='Download', command=self.start_download_thread).grid(row=4, column=0, columnspan=3)

    def browse_url_file(self):
        self.url_file.set(filedialog.askopenfilename())

    def browse_destination_folder(self):
        self.destination_folder.set(filedialog.askdirectory())

    def start_download_thread(self):
        threading.Thread(target=self.download_files).start()

    def download_files(self):
        urls = []
        with open(self.url_file.get(), 'r') as file:
            urls = file.readlines()

        self.progress['maximum'] = len(urls)
        self.progress['value'] = 0

        CTX = ssl.SSLContext()
        headers = { 'user-agent' : USERAGENT, 'Authorization' : 'Bearer ' + self.token.get() }

        for url in urls:
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
    app = Downloader()
    app.mainloop()
