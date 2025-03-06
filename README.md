Retro Tools
-----
This is a set of custom scripts I developed to help manage ROMs and emulators on systems running Batocera, SBC handhelds with custom firmware, Recalbox, retropie, etc.

It is intended for headless/remote use or when GUI-based actions are too repetitive or cumbersome.

TOOL LISTING
-----
1. rom_downloader.py - This is a script that will scrape a single webpage and download all the .zip files listed on it.
    * Supports multithreading/simultaneous downloads. Tested up to 5 concurrent downloads myself, be wary of throttling by the hosting provider and your disk I/O.
    * Supports retry of failed downloads (3x) - after 3 times the failed filename will be written to failed_downloads.txt so you can deal with it later.
    * Supports region filtering - as long as the content host specifies the region in the filename.


2. zip_to_chd.py - Tool for extracting .zip archives of games containing CUE/BIN or ISO files and using chdman to compress them for emulator use
    * Supports custom input/output directories
    * Supports custom path to CHDMAN binary
    * Prompts to delete original .zip files or not. Always cleans up extracted .cue/.bin/.iso files    

