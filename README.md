# EDMC_SpanshRouter

This plugin's purpose is to automatically copy to your clipboard the next waypoint on a route you planned using [Spansh](https://www.spansh.co.uk/plotter).

## Install

- If you're on Linux, you'll need to make sure that **xclip** is installed before using the plugin (`sudo apt-get xclip` on Debian based systems).
- Open your EDMC plugins folder - in EDMC settings, select "Plugins" tab, click the "Open" button.
- Create a folder inside the plugins folder and call it whatever you want, **SpanshRouter** for instance
- Download the latest release [here](https://github.com/CMDR-Kiel42/EDMC_SpanshRouter/releases/latest) and unzip it.
- Open the folder you created and put all the files and folders you extracted inside
- Restart EDMC

## How to use

You can either plot your route directly from EDMC by clicking the "Plot Route" button, or you can import a CSV file from [Spansh](https://www.spansh.co.uk/plotter)
You can also create your own CSV file, as long as it contains the columns "System Name" and "Jumps" (that last one is optional).
A valid CSV file could look like:

```csv
System Name,Jumps
Saggitarius A*,5
Beagle Point,324
```

You can also use a .txt file created with [EDTS](https://bitbucket.org/Esvandiary/edts/wiki/edts)

Once your route is plotted, and every time you reach a waypoint, the next one is automatically copied to your clipboard.

You just need to go to your Galaxy Map and paste it everytime you reach a waypoint.

If for some reason, your clipboard should be empty or containing other stuff that you copied yourself, just click on the **Next waypoint** button, and the waypoint will be copied again to your clipboard.

If you close EDMC, the plugin will save your progress. The next time you run EDMC, it will start back where you stopped.

Fly dangerous! o7

## Updates

When a new update is available, you will be prompted with a popup listing the last changes, and asking whether you wish to update or not. If you say yes, the update will be installed the next time you launch EDMC.

## Known Issues

At the moment, plotting a route while the game is running, and which begins from the system you're currently in, doesn't update your "next waypoint". If you're in that situation, a couple of solutions are available:

- Using the **down** button below the **Next waypoint**
- Performing a FSS Discovery Scan
- Go in our out of Supercruise
- Logging back in and out while EDMC is already running.
