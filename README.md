# EDMC_SpanshRouter
This plugin's purpose is to automatically copy to your clipboard the next waypoint on a route you planned using [Spansh](https://www.spansh.co.uk/plotter).


## Install

- Open your EDMC plugins folder - in EDMC settings, select "Plugins" tab, click the "Open" button.
- Create a folder inside the plugins folder called **SpanshRouter**
- Open the **SpanshRouter** folder and put **load.py** inside.
- Restart EDMC


## How to use

- Once you've plotted your route on [Spansh](https://www.spansh.co.uk/plotter), download the CSV file that it generates
- On EDMC, click the **Upload new route** button and choose your file
- The next waypoint is now copied into your clipboard! Simply paste it into your Galaxy Map, and *voilà*!

Once you reach your next waypoint, the plugin will automatically update your clipboard, so you just need to go to your Galaxy Map and paste it everytime you reach a waypoint.

If for some reason, your clipboard should be empty or containing other stuff that you copied yourself, just click on the **Next waypoint** button, and the waypoint will be copied again to your clipboard.

If you close EDMC, the plugin will save your progress. The next time you run EDMC, it will start back where you stopped.

Fly dangerous! o7


## Known Issues
At the moment, plotting a route while the game is running, and which begins from the system you're currently in, doesn't update your "next waypoint". If you're in that situation, a couple of solutions are available:

* Performing a FSS Discovery Scan
* Go in our out of Supercruise
* Logging back in and out while EDMC is already running.
