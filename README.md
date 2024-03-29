# Penzu Export
Export your journal entries from penzu.com to a csv file.  

This is a command line program written in Python that uses Selenium to iterate through your penzu.com journal entries and save them in an easily usable format. Penzu doesn't offer any developer API and the only data export option outputs a pdf, so this is intended as a better way to export your data for backup, analysis, importing in other software, etc.

## Setup

This assumes you have Python3 (and pip) installed, as well as Google Chrome. 

### Clone the repo
`git clone https://github.com/ianmcaulay/penzu-export`  
`cd penzu-export`

### Install requirements 
`pip install -r requirements.txt`  

## Usage
1. Run `python export_penzu_data.py {JOURNAl_ID}`.
2. In the new Chrome window Selenium opened, open a new tab and go to https://penzu.com/app/login. This must be in a **new**, **manually** opened tab, because in my experience Cloudflare always blocks login attempts from a tab that was automatically opened by Selenium.
3. Input username and password and login.
4. Switch back to the terminal running the script and press Enter.

To find a journal's journal ID, go to it's list of entries on penzu.com. The URL should look like this: https://penzu.com/journals/{JOURNAL_ID}/entries. The journal ID should look like this: 24766000.

The output is a csv called `penzu_entries.csv` with these columns:  
* `entry_id` - Penzu internal ID for each entry (I assume this is unique even across different journals but I don't know for sure)  
* `journal_id` - Penzu internal ID for each journal  
* `content` - The text content of the journal entry  
* `title` - The title of the entry (if no title is set Penzu defaults to the date)  
* `created_at` - The Penzu display created at, for me it's always in this format: `Thu. 1/1/1970 at 1:00am` (something like `"%a. %d/%m/%Y at %I:%M%p"` for string formatting, although note there are no leading zeros)  
* `fetched_at` - Unix epoch seconds at the time the script exported the entry  

## Issues
Sometimes the script finds no entries even on page 1 and immediately exits. Usually just re-running the script will fix this. I think this is due to trying to fetch the entries before the page has fully loaded.

HTML formatting in journal text is ignored, only the text is exported.

## Notes
There's a lot of manual sleeping for a hardcoded number of seconds to wait for pages to load, which can cause the script to go slower than necessary or crash when the page hasn't loaded yet. On average it takes about 2 seconds per journal entry (depending on your Internet speed), so unless you have many thousands of entries the speed isn't a major issue.

Developed and tested with Python3.10, but probably works with any version that includes f-strings (i.e. 3.6+).  

Tested on Mac, so the Selenium and Chrome driver stuff may be glitchy on another OS.  

This is a personal project, I have no affiliation with Penzu.  

