import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def date_compare(datetime_list, test_datetime):
	''' 
	Check a list of datetimes to see if they match a given date.
	
	Note time is not considered. Element is True as long as it is the same day
	Returns a list of bools the same length as datetime_list.
	'''
	return [test_datetime.date()==d.date() for d in datetime_list]

def scrape_nl_binpage(url):
	''' Download raw HTML from a given URL ''' 
	resp = requests.get(url)
	soup = BeautifulSoup(resp.text,features="html.parser")
	return soup.body.find('div', attrs={'class' : 'bin-collection-dates-container'}).text

def extract_dates_from_container(raw_text, bin_names):
	''' Take raw HTML from the container and parse out the dates as datetime objects. '''
	# convert bin names list into storage dict
	section_dict = {name:[] for name in bin_names}
	
	# split on double line breaks as this seems to separate the sections
	# return list of string 'sections'
	raw_text_list = raw_text.split("\n\n")
	# remove any empty strings from list
	while("" in raw_text_list):
		raw_text_list.remove("")
	
	# compile a regex for the date format
	date_regex = re.compile("\d{2}\s\w+\s\d{4}")
	
	# parse each bin name value for date strings
	# then convert to datetime.datetime objects
	# outer loop :: loop over each 'section' of text.
	for row in raw_text_list:
		# inner loop :: loop over each 'bin type'
		for s in section_dict.keys():
			# check if the bin type is inside the str
			if s in row:
				# if so, find all the dates in this section
				section_date_strings = date_regex.findall(row)
				n_dates = len(section_date_strings)
				# convert to datetime.datetime
				section_dict[s] = list(
								map(
									datetime.strptime, 
									section_date_strings, 
									["%d %B %Y"]*n_dates
								)
				)
			# fi
		# end bin type loop
	# end string list
	
	return section_dict

				
if __name__ == "__main__":
	# set essential variables
	url = "https://www.northlanarkshire.gov.uk/bin-collection-dates/000118099475/48405709"
	bin_types = [
		"General Waste",
		"Blue-lidded Recycling Bin",
		"Food and Garden",
		"Glass, Metals, Plastics and Cartons",
	]
	# scrape the page and get the dates
	raw_html = scrape_nl_binpage(url)
	bin_date_dict = extract_dates_from_container(raw_html, bin_types)

	# test if a given date (today?) has any bins
	# print a message for each bin that is due
	test_date = datetime(2022,10,31,10,30,22)
	test_date = datetime.today()
	bins_today = False
	for bin in bin_date_dict.keys():
		if any(date_compare(bin_date_dict[bin],test_date)):
			print(f"Bin today : {bin}")
			bins_today = True
	# if no bins due, tell user
	if not bins_today:
		print("No bins due today!")
