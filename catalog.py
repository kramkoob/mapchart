# catalog.py

# Contains catalog and degree info. PDF parsing of degree maps.

#	Classes:
#		CatalogHTMLParse
#		Catalog
#		CatalogYear
#		Degree

import requests
from html.parser import HTMLParser as hp

import common

DATA_PREFIX = "maps\\"
DATA_EXT = ".dat"
SITE_PREFIX = r"https://www.atu.edu/"
CATALOG_YEARS_URL = r"advising/degreemaps.php"

class CatalogHTMLParse(hp):
	#Base for the other catalog classes since their pages are structured almost identically. Inheritors MUST define a self.parse(self, data) method, called each time this class finds a result, and must also call CatalogHTMLParse.__init__(self, tablemode) in its own __init__ method, where tablemode is a boolean to slightly modify operation mode (for degree list pages, this should be True)
	def __init__(self, tablemode):
		hp.__init__(self)
		self.tablemode = tablemode
		self.check_text = False
		self.search_for_list = False
		self.search_for_maps = False
		self.get_text = False
		self.next_attr = ""

	def populate(self):
		# Initiate the page loading and parsing into useable data
		self.feed(requests.get(self.url).text)
	
	# 1) First searches for paragraph with matching text, or for opening table
	# 2) Then searches the following lists and 3) their elements
	# 4) Create a CatalogYear for each year found
	# 5) Stop searching when reach the end of the main content or table
		
	# The following functions perform the aforementioned sequence.
	def handle_starttag(self, tag, attrs):
		if (tag == "p" and not self.tablemode) or tag == "table": #1
			self.check_text = True
			self.search_for_list = self.search_for_list or self.tablemode
		if self.search_for_list and tag == "ul": #2
			self.search_for_maps = True
		if self.search_for_maps and tag == "a": #3
			self.get_text = True
			self.next_attr = attrs[0][1]
			
	def handle_endtag(self, tag):
		if self.search_for_list and (tag == "main" or tag == "table"):#5
			self.search_for_list = False
		if self.search_for_maps and tag == "ul": #2
			self.search_for_maps = False
		if self.get_text and tag == "a": #3
			self.get_text = False
	
	def handle_data(self, data):
		if self.check_text: #1
			self.search_for_list = data.startswith("Degree Maps by catalog year") or self.tablemode
			self.check_text = not self.search_for_list
		if self.get_text: #4
			self.parse(data, self.next_attr)

class Catalog(CatalogHTMLParse):
	# Contains every academic year catalog
	def __init__(self):
		CatalogHTMLParse.__init__(self, False)
		self.catalogyears = []
		self.url = SITE_PREFIX + CATALOG_YEARS_URL
		self.filename = DATA_PREFIX + "catalog" + DATA_EXT
	
	def parse(self, data, attr):
		# Called from CatalogHTMLParse
		self.catalogyears.append(CatalogYear(data, attr))
	
class CatalogYear(CatalogHTMLParse):
	# Contains the degrees offered from a catalog in a specific academic year
	def __init__(self, year, url):
		CatalogHTMLParse.__init__(self, True)
		self.degrees = []
		
		self.year = int(year[2:4]) #takes e.g. "2021-2022" and strips to an integer 21
		self.year_formatted = str(self.year) + "-" + str(self.year + 1) # "21-22"
		self.year_formatted_long = year # "2021-2022"
		# link is passed from html parser, but needs the domain in front of it since it's a local address
		self.url = SITE_PREFIX + url
		self.filename = DATA_PREFIX + "catalog" + str(self.year) + DATA_EXT
		
	def parse(self, data, attr):
		# Called from CatalogHTMLParse
		self.degrees.append(Degree(data, attr))

class Degree():
	# A degree. To-do: this is where PDF parsing happens
	def __init__(self, name, url):
		self.name = name
		self.url = SITE_PREFIX + url
