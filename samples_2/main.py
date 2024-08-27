# main.py (naughty_entries.py)
"""
Finds links to entries which were not translated in an earlier step.
Uses a bibmap to decode the entries it can
Creates a browser instance to pull URLS when it can't
Reports results

NOTE: Data files have been removed
"""

import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from typing import TextIO  # for typing


def main():
  """
  main function that sequences other functions
  """
  csv_infile, outfile = set_up()
  total_record_accumulator, no_match_accumulator, no_catalog_accumulator = identify_naughty_entries(csv_infile, outfile)
  report_results(total_record_accumulator, no_match_accumulator, no_catalog_accumulator)


def set_up() -> (TextIO, TextIO):
  """
  Sets up infiles and outfiles
  passes them as a return

  :return csv_infile: csv file to be read
  :return outfile: csv file to be written to
  """
  csv_infile_name = 'naughty_entries.csv'
  csv_infile = open(f'{csv_infile_name}', 'r')
  outfile = open('naughty_entries_matched.csv', 'w', encoding='utf-8')
  return csv_infile, outfile
  

def identify_naughty_entries(csv_infile: TextIO, outfile: TextIO) -> (int, int, int):
  """
  loops through entries in the csv infile,
  searches them for NO MATCH status or NOT FOUND status
  If NOT FOUND, parses and translates to 001
  If NO MATCH, passes. 
  If neither, searches the URL with a browser instance.

  :param csv_infile: csv file to be read
  :param outfile: csv file to be written to
  :return total_record_accumulator: total number of records processed
  :return no_match_accumulator: total number of records with NO MATCH status
  :return no_catalog_accumulator: total number of records with NO CATALOG status
  """
  
  total_record_accumulator = 0
  no_match_accumulator = 0
  no_catalog_accumulator = 0
  naughty = False

  print('online!')

  for line in csv_infile:
    total_record_accumulator += 1
    if re.search('NOT FOUND', line, re.IGNORECASE):
      line = line.strip()
      naughty = True
      # print(line)
      naughty_s_url = re.findall(',.+,', line, re.IGNORECASE)
      naughty_s_url = naughty_s_url[0]
      naughty_bib = re.findall('=b[0-9]+', naughty_s_url, re.IGNORECASE)
      # naughty_bib = naughty_bib[0]
      naughty_bib = str(naughty_bib)
      naughty_bib = naughty_bib[3:11]

      control_number = translate_to_001(naughty_bib)

      if control_number == 'NO MATCH':
        no_match_accumulator += 1
      else:
        koha_url = search_koha_with_control(control_number)

        if not re.search('pl\?biblionumber=', koha_url):
          koha_url = 'NO CATALOG ENTRY'
          no_catalog_accumulator += 1

        line = line[0:len(line)-9] + koha_url
        line = line.strip()

    print(line, file = outfile)
    # print(line)
    print(f'{total_record_accumulator}. {line}')
  return total_record_accumulator, no_match_accumulator, no_catalog_accumulator
 

def translate_to_001(naughty_bib):
  """
  Takes a bib number which is unmatched
  checks to see if it is in the processed_bitmap.csv with a loop

  :param naughty_bib: bib number which was not found with an original bitmap
  :return control_number: 001 returned from the bib number query
  """
  bitmap_name = 'processed_bitmap.csv'
  bitmap = open(f'{bitmap_name}', 'r')
  bitmatch = False
  for line in bitmap:
    line = line.strip()
    if line[0:8] == naughty_bib:
      bitmatch = True
      control_number = line[10:len(line)]
  if bitmatch == True:
    return control_number
  else:
    return 'NO MATCH'


def search_koha_with_control(control_number):
  """
  Creates a browser instance
  searches the field for that control number
  returns the url

  :param control_number: The control number s a search string
  :return koha_url: The url of the result
  """
  koha_starting_url = 'https://tallons.law.utexas.edu/cgi-bin/koha/opac-main.pl'

  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome(options=chrome_options)

  driver.get(koha_starting_url)
  time.sleep(1)  # adjust sleep parameters depending on the OPAC
  driver.find_element(By.ID, "translControl1").send_keys(f'\"{control_number}\"')
  driver.find_element(By.ID, "searchsubmit").click()
  time.sleep(3)
  koha_url = driver.current_url
  time.sleep(3)

  return koha_url


def report_results(total_record_accumulator, no_match_accumulator, no_catalog_accumulator):
  """
  Reports results at the end of the process
  Reports total accumulator results

  :param total_record_accumulator: total number of records processed
  :param no_match_accumulator: total number of records with no match
  :param no_catalog_accumulator: total number of records with no catalog entry
  """
  print(f'Total Records processed: {total_record_accumulator}')
  print(f'Total          NO MATCH: {no_match_accumulator}')
  print(f'Total  NO CATALOG ENTRY: {no_catalog_accumulator}')


main()
