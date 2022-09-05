# Get catalog years https://www.atu.edu/advising/degreemaps.php
# Get list of degree maps for catalog years https://www.atu.edu/advising/degreemaps-21-22.php
# Get degree map
# Rip data
# Make chart

# Database flow:
# /mapchart.py
# /catalog.pickle
# /[catalog year]/
# /[catalog year]/degrees/
# /[catalog year]/degrees/[course prefix].pickle
# /[catalog year]/courses/[course prefix][course number].pickle

# pickle: built-in Python module for serializing classes, objects etc., for storage

import requests
from html.parser import HTMLParser as hp
import pickle
import os

CATALOG_YEARS_URL = r"https://www.atu.edu/advising/degreemaps.php"
CATALOG_BASE_URL = r"https://www.atu.edu/advising/degreemaps-"
CATALOG_EXTENSION = r".php"

# This class is provided as a base for the other catalog classes since their data pages are structured almost identically. Inheritors MUST define a self.parse(self, data) method, called each time this class finds a result, and must also call CatalogHTMLParse.__init__(self, tablemode) in its own __init__ method, where tablemode is a boolean to slightly modify operation mode (for degree list pages, this should be True)
class CatalogHTMLParse(hp):
	def __init__(self, tablemode):
		hp.__init__(self)
		self.tablemode = tablemode
		self.check_text = False
		self.search_for_list = False
		self.search_for_maps = False
		self.get_text = False

	def populate(self, url):
		self.feed(requests.get(url).text)
		# 1) First searches for paragraph with matching text, or for opening table
		# 2) Then searches the following lists and 3) their elements
		# 4) Create a CatalogYear for each year found
		# 5) Stop searching when reach the end of the main content or table
		
	def handle_starttag(self, tag, attrs):
		if (tag == "p" and not self.tablemode) or tag == "table": #1
			self.check_text = True
			self.search_for_list = self.search_for_list or self.tablemode
		if self.search_for_list and tag == "ul": #2
			self.search_for_maps = True
		if self.search_for_maps and tag == "a": #3
			self.get_text = True
			
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
			self.parse(data)

class Catalog(CatalogHTMLParse):
	def __init__(self):
		CatalogHTMLParse.__init__(self, False)
		self.catalogyears = []
	
	def parse(self, data):
		self.catalogyears.append(CatalogYear(data))
    
class CatalogYear(CatalogHTMLParse):
	def __init__(self, year):
		CatalogHTMLParse.__init__(self, True)
		self.year = int(year[2:4])
		self.year_formatted = str(self.year) + "-" + str(self.year + 1)
		self.year_formatted_long = year
		# create degree url based on year
		self.url = CATALOG_BASE_URL + self.year_formatted + CATALOG_EXTENSION
		print(self.url)
		self.degrees = []
		
	def parse(self, data):
		self.degrees.append(Degree(data))
		
class Degree():
	def __init__(self, name):
		self.name = name

catalog = Catalog()
catalog.populate(CATALOG_YEARS_URL)
for catalogyear in catalog.catalogyears:
	catalogyear.populate(catalogyear.url)
	print(str(len(catalogyear.degrees)) + " degrees for " + catalogyear.year_formatted_long)
	
os.system("pause")