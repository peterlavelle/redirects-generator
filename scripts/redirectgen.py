#!/usr/bin/env python3

# accepts a csv file with the following 3 fields: source, destination, redirect_code
# source: the source url for the redirect (domain gets stripped and the path is preserved)
# destination: the destination url for the redirect (full url is preserved)
# redirect_code: the response code for the redirect (e.g, 301, 302)

# Bugs:
# https://stackoverflow.com/questions/20507228/python-how-do-i-use-dictreader-twice


import csv
from urllib3 import util
from urllib3.util import parse_url as parse_url
from urllib3.exceptions import LocationParseError as LocationParseError
import re
import argparse

#List of valid http redirect response codes for the script
valid_redirect_codes = ['301','302','307']

def CheckRedirectCode(valid_redirect_codes, items):
  """
  checks that the redirect_code field for each row in the csv is
  a valid one we can deal with by checking them against a list of valid ones
  """
   
  for item in items:
    #Skip over any blank rows where all 3 fields in the csv are not populated
    if(item['source'] != "" and item['destination'] != "" and item['redirect_code'] !=""):
      if item['redirect_code'] not in valid_redirect_codes:
        # We have an invalid item. Output its row number and return false
        # output the row number in the CSV where the mistake is.
        print(f"Row {items.line_num} in the input CSV file has an invalid redirect_code value of {item['redirect_code']}. Unable to continue.") 
        # output a list of valid redirect_code values
        print("Valid redirect_code values for this script are:")
        for code in valid_redirect_codes:
          print(code)
        return False

  # None of them seem invalid as we haven't returned False so far so return True
  return True

def ComposeRewrite(items):
  """ composes rewrite rules and returns them as a list """
  rewrite_rules=[] # list to hold our rewrite rules
  for item in items:
    #Skip any rows were all 3 fields are blank
    if(item['source']!= "" and item['destination'] != "" and item['redirect_code'] != ""):
      # compose a new rewrite rule and add it to the list
      
      # Grab the path part of the source url
      source_path = parse_url(item['source']).path

      # Escape URL encoded characters in the source path
      # Used this as a guide: https://serverfault.com/questions/1036007/syntax-for-apache-rewriterule-to-match-encoded-urls-to-fix-character-encodin
      source_path=re.sub('%','\\\\x', parse_url(item['source']).path)

      #Escape dots in the url
      source_path=str(source_path).replace('.', '\.')

      #Add regex to rule to match on trailing slash and non-trailing slash versions of a source path with a trailing slash present
      # e.g /peterlavelle and /peterlavelle/ should both match.
      source_path=re.sub('\/$','/?', source_path)

      #Strip trailing slash from urls with a query string
      # regex should only match on a "/" if that "/" is followed by a "?"
      if parse_url(item['source']).query != None:
        source_path=re.sub('\/(?=\?)','', source_path)

      #check if the source url includes a query string. if it does we'll need a rewritecond and rewriterule
      if parse_url(item['source']).query != None:
        #We have a path with a query string on it, so do a different rule
        rewrite_rules.append(f"<IfModule mod_rewrite.c>\nRewriteEngine On\nRewriteCond %{{REQUEST_URI}} ^{source_path}$\nRewriteCond %{{QUERY_STRING}} ^{parse_url(item['source']).query}$\nRewriteRule ^(.*)$ {parse_url(item['destination']).url} [R={item['redirect_code']},L,QSD]\n</IfModule>\n")
      else:
        # We don't have a path with a query string on it, do a RedirectMatch
        rewrite_rules.append(f"RedirectMatch {item['redirect_code']} ^{source_path}$ {parse_url(item['destination']).url}\n")
  return rewrite_rules


def RewriteRuleToFile(rules, output_file_path):
  """ write out rewrite rules to a file """
  with open(output_file_path, 'w') as file:
    file.writelines(rules)

try:
  # Setup command line argument support
  parser=argparse.ArgumentParser()
  parser.add_argument("-u", "--urls", help="path to csv file containting the redirect urls we want to process", required=True)
  parser.add_argument("-o", "--outfile", help="path for the file we want to output the finished redirects to", required=True)
  
  # Get the values passed to each command line argument
  args = parser.parse_args()

  csv_path = args.urls #Path the csv file containing the urls we want to process
  rewrites_output_file_path = args.outfile # path to write our actual redirects to
  

  # Open the CSV file for reading
  with open(csv_path, newline='') as csvfile:
    urls = csv.DictReader(csvfile) # Read rows from csv file into a dictionary
    # check we have a valid redirect code for each row before proceeding. Exit if any row contains an invalid redirect code
    if CheckRedirectCode(valid_redirect_codes=valid_redirect_codes, items=urls):
      #all rows contain a valid redirect code field. compose rewrites and write rewrite rules to a file
      csvfile.seek(0) # seek to beginning of the csv again as we'll need it again soon. see https://stackoverflow.com/questions/20507228/python-how-do-i-use-dictreader-twice
      RewriteRuleToFile(rules=ComposeRewrite(items=csv.DictReader(csvfile)), output_file_path=rewrites_output_file_path)
    else:
      # Exit with an error. We have an invalid redirect code in one of the rows.
      exit(1)


except FileNotFoundError as e:
  # Triggers if the csv file cannot be found
  print(f"{e.filename} does not exist. Unable to continue. Exiting.")
  exit(1)

except LocationParseError as e:
  #Triggers if we have a malformed url from the csv
  print(f"Malformed URL {e.location} found in the CSV file. Unable to continue. Exiting.")
  exit(1)

except PermissionError as e:
  # triggers when we encounter a permission denied error writing a file
  print(f"Permission denied reading from/writing to the file {e.filename} Unable to continue. Exiting")
  exit(1)