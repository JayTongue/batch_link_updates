# main.py (S_K_Translator_2.py)
"""
This code takes URLs from current the old Sierra ILS 
and looks them up in the new Koha ILS

NOTE: Data files have been removed
"""


import re
from typing import TextIO


def main():
  """
  Main function
  sequences call order and logic flow
  """
  asset_list_infile, outfile = set_up()
  line_counter = solicit_url_input(asset_list_infile, outfile)
  print_results(line_counter)


def set_up() -> (TextIO, TextIO):
  """
  Sets up infiles and outfiles
  passes them as a return

  :return asset_list_infile: CSV of assets
  :return outfile: file object that the rest of the function will print to
  """
  asset_list_infile = open('assets_list.csv', 'r')
  outfile_name = 'assets_translated.csv'
  outfile = open(outfile_name, 'w', encoding='utf-8')

  return asset_list_infile, outfile


def solicit_url_input(asset_list_infile: TextIO, outfile: TextIO) -> int:
  """
  Loops through the infile and sends rows to two processing functions
  returns the accumulated line counter

  :param asset_list_infile: CSV of assets
  :param outfile: file that will be printed to 
  :return line_counter: accumulated line counter to display results
  """
  line_counter = 0

  for line in asset_list_infile:
    line = line.strip()
    sierra_url = line[9:len(line)]
    sierra_key = process_sierra_link(sierra_url)
    koha_url = translate_to_koha(sierra_key)
    line = line + f',{koha_url}'
    print(line, file=outfile)
    line_counter += 1
    print(f'{line_counter}. {line}')

  return line_counter



def process_sierra_link(sierra_url: str) -> str:
  """
  Takes a full sierra URL
  parses it into just the key for searching

  :param sierra_url: full sierra URL
  :return sierra_key: parsed key for searching
  """
  regex_pattern = r'=b[0-9]+'
  sierra_key = str(re.findall(regex_pattern, sierra_url))
  sierra_key = '.' + sierra_key[3:11]
  print(sierra_key)
  return sierra_key


def translate_to_koha(sierra_key):
  """
  Takes sierra key and loops through a map object
  imports that map object and loops through it
  Detects matches and stores them with a boolean value

  :param sierra_key: the key parsed from the input file
  :returb koha_url: Either a valid URL or 'NOT FOUND' depending on whether or not it matches
  """
  infile_name = 'S_K_Map.csv'
  infile = open(f'{infile_name}', 'r')
  key_match = False
  koha_url = []
  for line in infile:
    sierra_line = line[1:10]
    if sierra_line == sierra_key :
      koha_line = line[14:len(line)-2]
      key_match = True
    if key_match == True:
      koha_url = f'https://tarlton.bywatersolutions.com/cgi-bin/koha/opac-detail.pl?biblionumber={koha_line}'
  if not key_match:
    koha_url = 'NOT FOUND'

  return koha_url


def print_results(line_counter):
  """
  Prints results at the end of the function

  :param line_counter: accumulated line counter to display results
  """
  print(f'Task Complete.\n{line_counter} lines processed.')


main()