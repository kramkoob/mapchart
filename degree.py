#!/usr/bin/python3

#Degree program access

# DEV to-do:
# 	Fill out semesters in degrees from accordions (_accordions_to_degrees)
# 	Degree descriptions (_accordions_to_degrees)

#Current:
#	https://www.atu.edu/catalog/dev/undergraduate/programs.php
#2022-2023
# https://www.atu.edu/catalog/2022-23/undergraduate/programs.php
#2019-2021 and prior
#	https://www.atu.edu/catalog/archive/undergraduate/2021/programs.php
#2016-2018
# https://www.atu.edu/catalog/archive/undergraduate/2016/live/programs.php
#Prior to 2015: pdf format

#from lib import cache, catalog
import cache, catalog

import requests
import bs4 as bs
from os.path import join

_url_degree_list = r'https://www.atu.edu/catalog/current/undergraduate/programs.php'
_url_root = r'https://www.atu.edu'

class Semester():
	def __init__(self, id, name):
		self.name = name
		self.id = id
		self.entries = list()
	def add_entry(self, entry):
		if isinstance(entry, catalog.course):
			self.entries.append(entry)

class Degree():
	def __init__(self, id, name):
		self.name = name
		self.id = id
		self.semesters = list()
	def add_semester(self, name):
		self.semesters.append(semester(len(self.semesters) + 1, name))
	def add_track(self, n):
		self.name = self.name + ' Track ' + str(n)

def _accordion_to_degrees(degreepage, degreelink):
	degreelist = []
	track = 0
	# find the div with accordion class
	accordionelements = degreepage.find_all('div', 'accordion')
	for _ in accordionelements:
		# create degree
		# name found from h1 header at top of page
		degree_name = degreepage.find('div', 'col-lg-8 mb-5').find('h1').get_text()
		# id is the link to the degree page
		degree_id = degreelink
		degree = Degree(degree_id, degree_name)
		# one major has two tracks listed on the same page. append track number if that's the case.
		if len(accordionelements) > 1:
			track = track + 1
			degree.add_track(track)
		degreelist.append(degree)
	return degreelist

def degrees():
	filename = 'undergrad.dat'
	try:
		degrees = cache.load(filename)
	except FileNotFoundError:
		print('Refreshing degrees, this may take some time...')
		degrees = []
		# load degree program page
		degreeindex = bs.BeautifulSoup(requests.get(_url_degree_list).text, 'lxml')
		# find the list element on the degree program page
		degreelist = degreeindex.find('div', id='panel-d21e114')
		degreelist.extend(degreeindex.find('div', id='panel-d21e1219'))
		# find every anchor tag's href (link) within the degree program list
		degreelinks = [_url_root + anchortag['href'] for anchortag in degreelist.find_all('a')]
		# download every linked page in the degree program list - presumably degree pages, but not always
		degreepages_texts = [requests.get(degreelink).text for degreelink in degreelinks]
		degreepages = [bs.BeautifulSoup(degreepage_text, 'lxml') for degreepage_text in degreepages_texts]
		for degreelink, degreepage in zip(degreelinks, degreepages):
			degrees.extend(_accordion_to_degrees(degreepage, degreelink))
		# create list of invalid pages
		notdegreelinks = [degreelink for degreelink in degreelinks if degreelink not in [degree.id for degree in degrees]]
		# try to find valid degrees in the remaining invalid pages
		for notdegreelink in notdegreelinks:
			# all these pages should already be downloaded, so find it
			notdegreepage = degreepages[degreelinks.index(notdegreelink)]
			# find the main content of the non-degree page
			notdegreepage_content = notdegreepage.find('div', 'col-lg-8 mb-5')
			# find all the anchor tags (links) in the non-degree page
			anchortags = notdegreepage_content.find_all('a')
			notdegreepage_links = []
			for anchortag in anchortags:
				try:
					anchortag_href = anchortag['href']
					# limit a little bit to what 
					if "#" not in anchortag_href and "catalog/" in anchortag_href:
						notdegreepage_links.append(anchortag_href)
				except KeyError:
					pass
			#	test each link to see if it is a degree page
			for degreelink in notdegreepage_links:
				testlink = _url_root + (degreelink[len(_url_root):] if _url_root in degreelink else degreelink)
				# if degree has not been found already, evaluate
				if testlink not in [degree.id for degree in degrees]:
					# download test page
					degreepage_text = requests.get(testlink).text
					degreepage = bs.BeautifulSoup(degreepage_text, 'lxml')
					# test if a program exists in that page
					degrees.extend(_accordion_to_degrees(degreepage, testlink))
				else:
					break
		# remove duplicates by link/id and name
		k = 0
		while k < len(degrees):
			if [degree.id for degree in degrees].count(degrees[k].id) > 1 or [degree.name for degree in degrees].count(degrees[k].name) > 1:
				del degrees[k]
				k -= 1
			k += 1
		# save final list to local cache
		cache.save(degrees, filename)
	print('Loaded ' + str(len(degrees)) + ' degrees')
	return degrees

if __name__ == '__main__':
	print('degree.py')
	term = catalog.terms()[2]
	degreelist = degrees()
	
