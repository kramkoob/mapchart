#!/usr/bin/python3
# Contains catalog and degree info. PDF parsing of degree maps.

import requests
from html.parser import HTMLParser as hp
import os
from os.path import join

import common

FILE_CATALOG_PREFIX = join("data", "catalog")
DATA_EXT = ".dat"
SITE_PREFIX = r"https://www.atu.edu/"
CATALOG_YEARS_URL = r"advising/degreemaps.php"

class CatalogHTMLParse(hp):
	'''Base class and handling functions for Catalog and CatalogYear'''
	#their pages are structured almost identically.
	#Inheritors MUST define a self.parse(self, data) method
	#Inheritors must also call CatalogHTMLParse.__init__(self, tablemode) in __init__
	#(tablemode is a boolean to slightly modify operation mode:
	#for degree list pages, this should be True)
	def __init__(self, tablemode):
		'''init. tablemode: adjust parsing. for CatalogYear, this should be True'''
		hp.__init__(self)
		self.tablemode = tablemode
		self.check_text = False
		self.search_for_list = False
		self.search_for_maps = False
		self.get_text = False
		self.next_attr = ""

	def populate(self):
		'''Load cached/download fresh data'''
		# Initiate the page loading and parsing into usable data
		try:
			loadfile = common.cache_load(self.filename)
			if self.tablemode == True:
				self.degrees = loadfile.degrees
				self.figure_year(loadfile.year_formatted_long)
			else:
				self.catalogyears = common.cache_load(self.filename).catalogyears
		except:
			self.feed(requests.get(self.url).text)
			try:
				common.cache_save_auto(self)
			except Exception:
				print("Unable to save catalog/catalog year")
	
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
	'''Entire catalog, containing years, therein containing degree maps'''
	def __init__(self):
		CatalogHTMLParse.__init__(self, False)
		self.catalogyears = []
		self.url = SITE_PREFIX + CATALOG_YEARS_URL
		self.filename = FILE_CATALOG_PREFIX + DATA_EXT
		print(self.filename)
	
	def parse(self, data, attr):
		'''Parse data from CatalogHTMLParse.handle_data'''
		self.catalogyears.append(CatalogYear(data, attr))
	
class CatalogYear(CatalogHTMLParse):
	'''A specific year from the catalog, containing degrees offered that year'''
	def __init__(self, year, url):
		'''init. Must pass catalog year and url to the year page'''
		CatalogHTMLParse.__init__(self, True)
		self.degrees = []
		self.figure_year(year)

		# link is passed from html parser, but needs the domain in front of it since it's a local address
		self.url = SITE_PREFIX + url
		self.file_prefix = FILE_CATALOG_PREFIX + str(self.year)
		self.filename = self.file_prefix + ".dat"
		print(self.filename)
		
	def figure_year(self, year):
		'''Calculate year in a few different formats'''
		self.year = int(year[2:4]) #takes e.g. "2021-2022" and strips to an integer 21
		self.year_formatted = str(self.year) + "-" + str(self.year + 1) # "21-22"
		self.year_formatted_long = year # "2021-2022"
	
	def parse(self, data, attr):
		'''Parse data from CatalogHTMLParse.handle_data'''
		self.degrees.append(Degree(data, attr, self.file_prefix))

class Degree():
	'''Degree (plan). PDF of degree stored and parsed in here'''
	def __init__(self, name, url, file_prefix):
		'''init. Must pass name of degree, url to pdf, and catalog year file prefix'''
		self.name = name
		self.url = SITE_PREFIX + url
		self.filename = join(file_prefix, os.path.basename(url).split('/')[-1])
	
	def populate(self):
		'''Load cached/download and save degree PDF contents'''
		try:
			self.file = common.cache_load(self.filename)
		except FileNotFoundError:
			self.file = requests.get(self.url).content
			common.cache_save(self.file, self.filename)
		except Exception:
			print("Unable to save degree file")
			
if __name__ == "__main__":
	print("catalog.py test")
	test_catalog = Catalog()
	test_catalog.populate()
	test_catalogyear = test_catalog.catalogyears[0]
	test_catalogyear.populate()
	test_degrees = test_catalogyear.degrees
	for degree in test_degrees:
		print(degree.name)
		print(degree.url)
		print(degree.filename)
		degree.populate()
