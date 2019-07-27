#!/usr/bin/env python2

import os
import requests
import zipfile

class SpanshUpdater():
    def __init__(self, version):
        self.version = version
        self.zip_name = "EDMC_SpanshRouter_" + version.replace('.', '') + ".zip"
        self.zip_downloaded = False

    def download_zip(self):
        url = 'https://github.com/CMDR-Kiel42/EDMC_SpanshRouter/releases/download/v' + self.version + '/' + self.zip_name

        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(self.zip_name, 'wb') as f:
                    f.write(r.content)
                self.zip_downloaded = True
            else:
                sys.stderr.write("Failed to fetch SpanchRouter update. Status code: " + str(r.status_code))
                self.zip_downloaded = False
        except NameError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            sys.stderr.write(''.join('!! ' + line for line in lines))
            self.zip_downloaded = False

    def install(self):
        if self.zip_downloaded:
            try:
                with zipfile.ZipFile(self.zip_name, 'r') as zip_ref:
                    zip_ref.extractall("./")

                os.remove(self.zip_name)
            except NameError:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                sys.stderr.write(''.join('!! ' + line for line in lines))