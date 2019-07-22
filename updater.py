#!/usr/bin/env python2

import os
import requests
import sys
import argparse
import time
import zipfile

def is_running(pid):        
    try:
        os.kill(pid, 0)
    except OSError:
        return False

    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pid')
    parser.add_argument('--version')
    
    args = parser.parse_args()
    pid = args.pid
    version = args.version

    zip_name = "EDMC_SpanshRouter_" + args.version.replace('.', '') + ".zip"
    url = 'https://github.com/CMDR-Kiel42/EDMC_SpanshRouter/releases/download/v' + args.version + '/' + zip_name
    r = requests.get(url)
    with open(zip_name, 'wb') as f:
        f.write(r.content)

    while is_running(int(pid)):
        time.sleep(.25)
    
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall("./")
        
    os.remove(zip_name)

if __name__ == "__main__":
    main()
