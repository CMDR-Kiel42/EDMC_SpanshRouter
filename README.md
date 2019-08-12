# EDMC_SpanshRouter

This plugin's purpose is to automatically copy to your clipboard the next waypoint on a route you planned using [Spansh](https://www.spansh.co.uk/plotter).

## Install

- If you're on Linux, you'll need to make sure that **xclip** is installed before using the plugin (`sudo apt-get xclip` on Debian based systems).
- Download the latest release [here](https://github.com/CMDR-Kiel42/EDMC_SpanshRouter/releases/latest) and unzip it.
- Open your EDMC plugins folder - in EDMC settings, select "Plugins" tab, click the "Open" button.
- Create a folder inside the plugins folder called **SpanshRouter**
- Open the **SpanshRouter** folder you created and put all the files you extracted inside.
- Restart EDMC

## How to use

You can either plot your route directly from EDMC, or you can import a CSV file from [Spansh](https://www.spansh.co.uk/plotter)

Once your route is plotted, and every time you reach a waypoint, the next one is automatically copied to your clipboard.

You just need to go to your Galaxy Map and paste it everytime you reach a waypoint.

If for some reason, your clipboard should be empty or containing other stuff that you copied yourself, just click on the **Next waypoint** button, and the waypoint will be copied again to your clipboard.

If you close EDMC, the plugin will save your progress. The next time you run EDMC, it will start back where you stopped.

Fly dangerous! o7

## Updates

When a new update is available, it will automatically be downloaded. You'll just have to restart EDMC to install it.

## Known Issues

At the moment, plotting a route while the game is running, and which begins from the system you're currently in, doesn't update your "next waypoint". If you're in that situation, a couple of solutions are available:

- Using the **down** button below the **Next waypoint**
- Performing a FSS Discovery Scan
- Go in our out of Supercruise
- Logging back in and out while EDMC is already running.
