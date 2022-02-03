import datetime as dt
import os
import sys
import time

import jinja2
import pandas as pd

#
# Settings
#

# Project settings

# project_dir = os.getcwd()
project_dir = os.path.dirname(os.path.realpath(__file__))

template_dir = f"{project_dir}/templates"
data_dir = f"{project_dir}/data"
output_dir = f"{project_dir}/output"

# Runtime options

SHEET_ID = None

# Make an API request, or load cached data from a previous run?
USE_CACHE = False

if (len(sys.argv)==1) or (len(sys.argv)>3):
    raise RuntimeError(f'Parameters: SHEET_ID [--cached]')

for arg in sys.argv[1:]:
    if arg in ['-c', '--cached']:
        USE_CACHE = True
    else:
        SHEET_ID = arg

if USE_CACHE:
    print("Skipping API request.")
else:
    # This assumes the sheet is publicly readable.
    data = pd.read_excel(f"https://docs.google.com/spreadsheets/export?id={SHEET_ID}&exportFormat=xlsx",
                         dtype=str) # To preserve the specific format as best we can --
                                    # our types vary for each row.
    # Write to local cache
    os.makedirs(data_dir, exist_ok=True)
    data.to_csv(f"{data_dir}/data.csv", index=False)

#
# Prepare the data
#

data = pd.read_csv(f"{data_dir}/data.csv")
values = data.set_index('MetricID').Value.to_dict()

ctx = {} # Template context dict
ctx['today'] = dt.datetime.now()

ctx.update(values) # Add our metrics 

#
# Generate the page
# 

# Jinja2 filters to format dates.
def format_date(date):
    if date is None:
        return None
    # Unfortunately, Python has no cross-platform strftime code for day-of-month 
    # without leading zeros -- so we need to mix and match our formatting.
    # return date.strftime('%d %B %Y')
    return date.strftime(f"{date.day} %B %Y")

def format_long_date(date):
    if date is None:
        return None
    # return date.strftime('%A, %d %B %Y')
    return date.strftime(f"%A, {date.day} %B %Y")

def format_long_datetime(date):
    if date is None:
        return None
    # return date.strftime('%A, %d %B %Y at %H:%M')
    return date.strftime(f"%A, {date.day} %B %Y at %H:%M")

# Jinja2 filter to apply thousands separator, no decimal places.
def format_thousands(value):
    if value is None:
        return None
    return '{:,}'.format(int(value))

# Jinja2 filter to format percentage, no decimal places.
# First remove any percentage signs that may still be included.
def format_percent(value):
    if value is None:
        return None
    if type(value)==str:
        value = value.strip('%')
    return '{:,}'.format(float(value))

j2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    trim_blocks=True)

j2_env.filters['thousands'] = format_thousands
j2_env.filters['percent'] = format_percent
j2_env.filters['date'] = format_date
j2_env.filters['long_date'] = format_long_date
j2_env.filters['long_datetime'] = format_long_datetime

os.makedirs(output_dir, exist_ok=True)
with open(f"{output_dir}/index.html", 'w', encoding='utf-8') as f:
    f.write(j2_env.get_template('text.html.j2').render(ctx))
