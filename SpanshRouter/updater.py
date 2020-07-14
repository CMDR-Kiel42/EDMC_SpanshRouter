import os
import requests
import zipfile
import sys
import traceback
import json
import tkinter as tk
import tkinter.font as tkfont
import tkinter.scrolledtext as ScrolledText

class SpanshUpdater():
    def __init__(self, version, plugin_dir):
        self.version = version
        self.zip_name = "EDMC_SpanshRouter_" + version.replace('.', '') + ".zip"
        self.plugin_dir = plugin_dir
        self.zip_path = os.path.join(self.plugin_dir, self.zip_name)
        self.zip_downloaded = False
        self.changelogs = self.get_changelog()

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
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            sys.stderr.write(''.join('!! ' + line for line in lines))
            self.zip_downloaded = False
        finally:
            return self.zip_downloaded

    def install(self):
        if self.download_zip():
            try:
                with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.plugin_dir)

                os.remove(self.zip_path)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                sys.stderr.write(''.join('!! ' + line for line in lines))
        else:
            sys.stderr.write("Error when downloading the latest SpanshRouter update")

    def get_changelog(self):
        url = "https://api.github.com/repos/CMDR-Kiel42/EDMC_SpanshRouter/releases/latest"
        try:
            r = requests.get(url, timeout=2)
            
            if r.status_code == 200:
                # Get the changelog and replace all breaklines with simple ones
                changelogs = json.loads(r.content)["body"]
                changelogs = "\n".join(changelogs.splitlines())
                return changelogs

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            sys.stderr.write(''.join('!! ' + line for line in lines))


class UpdatePopup(tk.Toplevel):
    def __init__(self, changelogs):
        super().__init__()
        width, height = 600, 280
        x = self.winfo_screenwidth()/2 - width/2
        y = self.winfo_screenheight()/2 - height/2
        self.geometry("%dx%d+%d+%d" % (width, height, x, y))
        self.title("SpanshRouter - Update available")
        self.text_field = ScrolledText.ScrolledText(self, wrap="word", height=10)
        self.text_field.tag_configure("title", font=tkfont.Font(weight="bold", size=14), justify=tk.CENTER)

        for line in changelogs.splitlines():
            if line.startswith("## "):
                line = line.replace("## ", "SpanshRouter - Release ")
                self.text_field.insert(tk.END, line + "\n", "title")
            else:
                self.text_field.insert(tk.END, line + "\n")

        self.skip_install_checkbox = tk.Checkbutton(self, text="Do not warn me about this version anymore")
        self.install_button = tk.Button(self, text="Install")
        self.cancel_button = tk.Button(self, text="Cancel")
            
        self.text_field.config(state=tk.DISABLED)
        self.text_field.grid(row=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, padx=10, pady=15)
        self.skip_install_checkbox.grid(row=1, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
        self.install_button.grid(row=2, column=0, pady=15)
        self.cancel_button.grid(row=2, column=1)
            


if __name__ == "__main__":
    print("Testing")
    sp_updater = SpanshUpdater("3.0.3", ".")
    root = tk.Tk()
    root.geometry("200x300") 
    root.title("main")
    popup = UpdatePopup(sp_updater.changelogs)
    popup.mainloop()