#!/usr/bin/env python2

import os
import requests
import zipfile
import sys
import traceback

class SpanshUpdater():
    def __init__(self, version, plugin_dir):
        self.version = version
        self.zip_name = "EDMC_SpanshRouter_" + version.replace('.', '') + ".zip"
        self.plugin_dir = plugin_dir
        self.zip_path = os.path.join(self.plugin_dir, self.zip_name)
        self.zip_downloaded = False

    def download_zip(self):
        url = 'https://github.com/CMDR-Kiel42/EDMC_SpanshRouter/releases/download/v' + self.version + '/' + self.zip_name

        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(self.zip_path, 'wb') as f:
                    print("Downloading SpanshRouter to " + self.zip_path)
                    f.write(os.path.join(r.content))
                self.zip_downloaded = True
            else:
                sys.stderr.write("Failed to fetch SpanchRouter update. Status code: " + str(r.status_code))
                self.zip_downloaded = False
        except NameError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            sys.stderr.write(''.join('!! ' + line for line in lines))
            self.zip_downloaded = False
        finally:
            return self.zip_downloaded

    def install(self):
        if self.zip_downloaded:
            try:
                with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.plugin_dir)

                os.remove(self.zip_path)
            except NameError:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                sys.stderr.write(''.join('!! ' + line for line in lines))