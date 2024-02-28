import argparse
from pathlib import Path
import re
import time

import pandas as pd
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc


# All sleep times are in seconds.
SLEEP_AFTER_LOGIN = 1
SLEEP_AFTER_PAGE_LOAD = 1
MAX_TIMEOUT = 30
ENTRIES_CSV = Path('penzu_entries.csv')
ENTRY_URL_PATTERN = re.compile(r'https://penzu.com/journals/(\d*)/(\d*)')


class Entry:

    def __init__(self, entry_url, created_at):
        self.entry_url = entry_url
        self.created_at = created_at
        self.journal_id, self.entry_id = ENTRY_URL_PATTERN.match(entry_url).groups()


def get_only_element(lst):
    assert len(lst) == 1, f'Expected length 1, got length {len(lst)} in list {lst}.'
    return lst[0]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('journal_id',
                        help='Journal ID of Penzu journal to export (should look something like this: 24766000)')
    return parser.parse_args()


def get_url(driver, url):
    driver.get(url)
    wait_for_page_load(driver)


def wait_for_page_load(driver):
    loader = driver.find_element(By.CLASS_NAME, 'global-loader__wrap')
    finished_loader_classes = {'global-loader__wrap', 'ng-hide'}
    time.sleep(5)
    t0 = time.time()
    while time.time() - t0 < MAX_TIMEOUT and set(loader.get_attribute('class').split(' ')) != finished_loader_classes:
        time.sleep(.1)
        loader = driver.find_element(By.CLASS_NAME, 'global-loader__wrap')
    time.sleep(SLEEP_AFTER_PAGE_LOAD)


def get_driver():
    driver = uc.Chrome(use_subprocess=True)
    return driver


def get_entries_df():
    if ENTRIES_CSV.exists():
        df = pd.read_csv(ENTRIES_CSV, dtype={'entry_id': str})
    else:
        df = pd.DataFrame(columns=[
            'journal_id',
            'entry_id',
            'content',
            'title',
            'created_at',
            'fetched_at'])
    df = df.set_index('entry_id')
    return df


def get_entries_from_entries_url(driver, entries_url):
    get_url(driver, entries_url)
    entries = []
    for entry_element in driver.find_elements(By.CLASS_NAME, 'entries-list__item'):
        entry_title_element = get_only_element(entry_element.find_elements(By.CSS_SELECTOR, '.title.item__cell'))
        entry_url_element = get_only_element(entry_title_element.find_elements(By.TAG_NAME, 'a'))
        entry_url = entry_url_element.get_attribute('href')
        created_at_element = get_only_element(entry_element.find_elements(By.CSS_SELECTOR, '.date.item__cell'))
        created_at = created_at_element.text
        entries.append(Entry(entry_url, created_at))

    return entries


def retry_get_entries_from_entries_url(driver, entries_url):
    max_retries = 3
    while max_retries > 0:
        try:
            return get_entries_from_entries_url(driver, entries_url)
        except StaleElementReferenceException as e:
            max_retries -= 1
            if max_retries <= 0:
                raise e
            print('WARNING: Stale element exception, sleeping and retrying...')
            time.sleep(3)


def get_all_entries(driver, journal_id):
    curr_page = 1
    # Temporarily set next_entry_urls to dummy truthy value to enter loop.
    next_entry_urls = True
    while next_entry_urls:
        print(f'Fetching entries from page {curr_page}')
        entries_url = f'https://penzu.com/journals/{journal_id}/entries?page={curr_page}'
        next_entry_urls = retry_get_entries_from_entries_url(driver, entries_url)
        yield from next_entry_urls
        curr_page += 1
    print(f'Found no more entries at page {curr_page - 1}')


def get_entry_data(driver, entry):
    get_url(driver, entry.entry_url)
    text_element = get_only_element(driver.find_elements(By.CLASS_NAME, 'cke_inner'))
    text = text_element.text
    title_element = get_only_element(driver.find_elements(By.CLASS_NAME, 'h1'))
    title = title_element.get_property('value')

    entry_data = {
        'journal_id': entry.journal_id,
        'entry_id': entry.entry_id,
        'content': text,
        'title': title,
        'created_at': entry.created_at,
        'fetched_at': time.time(),
    }
    return entry_data


def save_entry_data(entry_data):
    new_df = pd.DataFrame([entry_data])
    new_df = new_df.set_index('entry_id')
    mode = 'w' if not ENTRIES_CSV.exists() else 'a'
    include_header = not ENTRIES_CSV.exists()
    new_df.to_csv(ENTRIES_CSV, header=include_header, mode=mode)


def get_all_entries_data(journal_id):
    df = get_entries_df()
    driver = None
    try:
        driver = get_driver()
        input('Open a new tab, visit https://penzu.com/app/login and login and press enter...')
        driver.switch_to.window(driver.current_window_handle)
        num_new_entries = 0
        for entry in get_all_entries(driver, journal_id):
            if entry.entry_id in df.index:
                print(f'Skipping entry {entry.entry_id} which has already been fetched')
            else:
                print(f'Fetching entry {entry.entry_id}')
                entry_data = get_entry_data(driver, entry)
                save_entry_data(entry_data)
                num_new_entries += 1
        print(f'Total number of entries: {len(df) + num_new_entries} (added {num_new_entries} new entries)')
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    args = get_args()
    get_all_entries_data(args.journal_id)
