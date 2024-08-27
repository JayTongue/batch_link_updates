# main.py. (nice_entries_verifier.py)
"""
This code verifies entries from a list. 
Generates another CSV which should be easily readable and shared
or opened in alternative software
"""

from urllib.request import urlopen
from typing import TextIO
import re
import time


def main():
  """
  Main function for 
  calls other functions in sequence
  """

  infile, outfile = set_up()
  search_infile(infile, outfile)


def set_up() -> (TextIO, TextIO):
  """
  Sets up a files containing links for processing
  Sets up file for results to be written to

  :return infile: A CSV of links to be read into the program
  :return outfile: A CSV where verified entires will be written
  """

  infile = open('all_nice_entries.csv', 'r')
  outfile = open('entries_verified.csv', 'w', encoding='utf-8')
  return infile, outfile


def search_infile(infile: TextIO, outfile: TextIO):
  """
  A primary loop which will send each link in the infile to a web verification sub-function.
  Uses accumulators to output data for both monitoring and final records.
  Parses lines from infile and distributes them to sub-function and print statements

  :param infile: The CSV file with records to be verified
  :param outfile: the file into which results will be stored
  """

  line_counter = 0
  verified_lines = 0
  problematic_lines = 0

  for line in infile:
    line_counter += 1
    line = line.strip()
    line_list = line.split(',')
    koha_url = line_list[2]

    corrected_line, verified_lines, problematic_lines = web_verification(
      line, koha_url, verified_lines, problematic_lines)

    print(corrected_line, file=outfile)
    print(line_counter, verified_lines, problematic_lines)


def web_verification(line: str, koha_url: str, verified_lines: int,
                     problematic_lines: int) -> (str, int, int):
  """
  Attempts to create a selenium browser instance to search a provided URL. 
  Searches the returned page for bibliographic information.
  Uses a Try/Except block to catch errors with the URL
  Marks verified and problematic entry rows.
  Obviously,  will have to be changed depending on each OPAC.

  :param line: The line of total information from the CSV. Not parsed here.
  :param koha_url: the URL from the looped line.
  :param verified_lines: the counter for verified lines
  :param problematic_lines: the counter for problematic lines
  :return corrected_line: The original CSV line with status appended
  :return verified_lines: Adjusted accumulator for verified lines
  :return problematic_lines: Adjusted accumulator for problematic lines

  >>> line = '19665471,https://tallons.law.utexas.edu/record=b1451493~S0,https://tallons.law.utexas.edu/cgi-bin/koha/opac-detail.pl?biblionumber=141304'
  >>> koha_url = https://tallons.law.utexas.edu/cgi-bin/koha/opac-detail.pl?biblionumber=141304
  >>> verified_lines = 5
  >>> problematic_lines = 5
  >>> web_verification(line, koha_url, verified_lines, problematic_lines)
('19665471,https://tallons.law.utexas.edu/record=b1451493~S0,https://tallons.law.utexas.edu/cgi-bin/koha/opac-detail.pl?biblionumber=141304,VERIFIED', 6, 5)

  >>> koha_url = '19666427,https://tallons.law.utexas.edu/record=b1528559~S0,https://tarlton.bywatersolutions.com/cgi-bin/koha/opac-detail.pl?biblionumber=243313'
  >>> verified_lines = 5
  >>> problematic_lines = 5
  >>> web_verification(line, koha_url, verified_lines, problematic_lines)
('19666427,https://tallons.law.utexas.edu/record=b1528559~S0,https://tarlton.bywatersolutions.com/cgi-bin/koha/opac-detail.pl?biblionumber=243313,PROBLEMATIC', 5, 6)')
  """
  clean_title = ''
  clean_author = ''

  try:
    page = urlopen(koha_url)
    koha_html = page.read().decode('utf-8')
    time.sleep(
      3)  # Adjust sleep parameters depending on website DOS protections

    title_regex_pattern = r'<h1 class="title" property="name">.*?<.*?>'
    title_match_results = re.findall(title_regex_pattern, koha_html,
                                     re.IGNORECASE)
    clean_title = re.sub(r'<.*?>', '', str(title_match_results))
    clean_title = clean_title[1:len(clean_title) - 1]
    clean_title = clean_title.replace('&amp;', '&')

    author_regex_pattern = r'<span property=".*?" typeof=".*?"><span property="name">.*?</span></span>'
    author_match_results = re.findall(author_regex_pattern, koha_html,
                                      re.IGNORECASE)
    clean_author = re.sub(r'<.*?>', '', str(author_match_results))
    clean_author = clean_author[1:len(clean_author) - 1]

    corrected_line = line + ',VERIFIED'
    verified_lines += 1

  except:
    corrected_line = line + ',PROBLEMATIC'
    problematic_lines += 1

  return corrected_line, verified_lines, problematic_lines


main()
