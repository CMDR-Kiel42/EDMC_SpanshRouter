import os
import requests
import zipfile
import sys
import traceback
import json
import tkinter as tk
import tkinter.font as tkfont
import tkinter.scrolledtext as ScrolledText
import tkinter.messagebox as confirmDialog


class SpanshUpdater():
    def __init__(self, plugin_dir):
        version_file = os.path.join(plugin_dir, "version.json")
        with open(version_file, 'r') as version_fd:
            self.plugin_version = version_fd.read()

        self.latest_version = self.plugin_version
        self.zip_name = "EDMC_SpanshRouter_VERSION.zip"
        self.plugin_dir = plugin_dir
        self.zip_path = None
        self.zip_downloaded = False
        self.changelogs = self.get_changelog()
        self.update_popup = UpdatePopup(self)
        self.update_popup.withdraw()
        self.update_available = False

    def download_zip(self):
        url = 'https://github.com/CMDR-Kiel42/EDMC_SpanshRouter/releases/download/v' + self.latest_version + '/' + self.zip_name

        try:
            print("Downloading SpanshRouter to " + self.zip_path)
            r = requests.get(url)
            if r.status_code == 200:
                print("Download successful.")
                with open(self.zip_path, 'wb') as f:
                    f.write(os.path.join(r.content))
                self.zip_downloaded = True
            else:
                sys.stderr.write("Failed to fetch SpanshRouter update. Status code: " + str(r.status_code) + '\n')
                sys.stderr.write("Download URL: " + url + '\n')
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
                print("Successfully installed SpanshRouter version " + self.latest_version)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                sys.stderr.write(''.join('!! ' + line for line in lines))
        else:
            sys.stderr.write("Error when downloading the latest SpanshRouter update")

    def cleanup_old_version(self):
        try:
            if (os.path.exists(os.path.join(self.plugin_dir, "AutoCompleter.py"))
            and os.path.exists(os.path.join(self.plugin_dir, "SpanshRouter"))):
                files_list = os.listdir(self.plugin_dir)

                for filename in files_list:
                    if (filename != "load.py"
                    and (filename.endswith(".py") or filename.endswith(".pyc") or filename.endswith(".pyo"))):
                        os.remove(os.path.join(self.plugin_dir, filename))
        except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                sys.stderr.write(''.join('!! ' + line for line in lines))

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

    def ask_for_update(self):
        self.update_popup.deiconify()

    def check_for_update(self):
        self.cleanup_old_version()
        version_url = "https://raw.githubusercontent.com/CMDR-Kiel42/EDMC_SpanshRouter/master/version.json"
        try:
            response = requests.get(version_url, timeout=2)
            if response.status_code == 200:
                if self.plugin_version != response.text:
                    self.update_available = True
                    self.latest_version = response.text
                    self.zip_name = self.zip_name.replace("VERSION", self.latest_version.replace('.', ''))
                    self.zip_path = os.path.join(self.plugin_dir, self.zip_name)

            else:
                sys.stderr.write("Could not query latest SpanshRouter version: " + str(response.status_code) + response.text)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            sys.stderr.write(''.join('!! ' + line for line in lines))


class UpdatePopup(tk.Toplevel):
    def __init__(self, sp_updater):
        self.sp_updater = sp_updater
        super().__init__()
        width, height = 600, 280
        x = self.winfo_screenwidth()/2 - width/2
        y = self.winfo_screenheight()/2 - height/2
        self.geometry("%dx%d+%d+%d" % (width, height, x, y))
        self.title("SpanshRouter - Update available")
        self.text_field = ScrolledText.ScrolledText(self, wrap="word", height=10)
        self.text_field.tag_configure("title", font=tkfont.Font(weight="bold", size=14), justify=tk.CENTER)

        for line in sp_updater.changelogs.splitlines():
            if line.startswith("## "):
                line = line.replace("## ", "SpanshRouter - Release ")
                self.text_field.insert(tk.END, line + "\n", "title")
            else:
                self.text_field.insert(tk.END, line + "\n")

        self.skip_install_checkbox = tk.Checkbutton(self, text="Do not warn me about this version anymore")
        self.install_button = tk.Button(self, text="Install", command=self.click_install)
        self.cancel_button = tk.Button(self, text="Cancel", command=self.click_cancel)
            
        self.text_field.config(state=tk.DISABLED)
        self.text_field.grid(row=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, padx=10, pady=15)
        self.skip_install_checkbox.grid(row=1, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
        self.install_button.grid(row=2, column=0, pady=15)
        self.cancel_button.grid(row=2, column=1)

    def click_install(self):
        self.sp_updater.update_available = True
        self.destroy()
        confirmDialog.showinfo("SpanshRouter", "The update will be installed as soon as you quit EDMC.")
    
    def click_cancel(self):
        self.sp_updater.update_available = False
        self.destroy()
