# Penzu Export
Export your journal entries from penzu.com to a csv file. 

## Setup

### Clone the repo
`git clone https://github.com/ianmcaulay/penzu-export`  
`cd penzu-export`

### Make a virtual environment (optional)
Use whatever virtual environment you prefer. For example with virtualenv:  
`virtualenv env`  
`source env/bin/activate`

### Install requirements 
`pip install -r requirements.txt`  
The script uses Selenium which requires the correct chrome driver binary to work. If you upgrade your version of Google Chrome and the script no longer works, run this to automatically update the driver:  
`pip install --upgrade --force-reinstall chromedriver-binary-auto`

## Usage
`python export_penzu_data.py JOURNAl_ID LOGIN_EMAIL LOGIN_PASSWORD`  
Optionally add the `--headless` flag to run Selenium in headless mode (i.e. without displaying a window). 

To find a journal's journal ID, go to it's list of entries. The URL should look like this: https://penzu.com/journals/{JOURNAL_ID}/entries. The journal ID should look something like this: 24766000.

The output is a csv called `penzu_entries.csv` with these columns:  
`entry_id` - Penzu interal ID for each entry (I assume this is unique even across different journals but I don't know for sure)  
`journal_id` - Penzu interal ID for each journal  
`content` - The text content of the journal entry  
`title` - The title of the entry (if no title is set Penzu defaults to the date)  
`created_at` - The Penzu display created at, for me it always looks like `Thu. 1/1/1970 at 1:00am` (something like `"%a. %d/%m/%Y at %I:%M%p"` for string formatting, although note there are no leading zeros)  
`fetched_at` - Unix epoch seconds at the time the script exported the entry  

## Issues
Sometimes the script finds no entries even on page 1 and immediately exits. Usually just re-running the script will fix this, or try removing the `--headless` flag. I think it has something to do with trying to fetch the entries before the page has fully loaded.

HTML formatting in journal text is ignored, only the text is exported.

## Notes
This is a personal project, I have no affiliation with Penzu.  

There's a lot of manual sleeping for a hardcoded number of seconds to wait for pages to load, which can cause the script to go slower than necessary or crash when 

Developed and tested with Python3.9, should probably work with any version that includes f-strings (i.e. 3.6+).  

Tested on Mac, so the Selenium stuff might be glitchy on another OS.  
