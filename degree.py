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

from lib import cache, catalog

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
	def __init__(self, id, name, term):
		self.name = name
		self.id = id
		self.term = term
		self.semesters = list()
	def add_semester(self, name):
		self.semesters.append(semester(len(self.semesters) + 1, name))
	def add_track(self, n):
		self.name = self.name + ' Track ' + str(n)

def _accordion_to_degrees(degreepage, degreelink):
	degreelist = list()
	# find the div with accordion class
	accordionelements = degreepage.find_all('div', 'accordion')
	for _ in accordionelements:
		# create degree
		# name found from h1 header at top of page
		degree_name = degreepage.find('div', 'col-lg-8 mb-5').find('h1').get_text()
		# id is the link to the degree page
		degree_id = degreelink
		degree = Degree(degree_id, degree_name, term)
		# one major has two tracks listed on the same page. append track number if that's the case.
		degree.add_track(k + 1) if len(accordionelements) > 1 else pass
		degreelist.append(degree)
	return degreelist

def degrees(term):
	filename = join(term.id, 'degrees.dat')
	try:
		degrees = cache.load(filename)
	except:
		print('Refreshing degrees for ' + term.name + ', this may take some time...')
		degrees = []
		# load degree program page
		degreeindex = bs.BeautifulSoup(requests.get(_url_degree_list).text, 'lxml')
		# find the list element on the degree program page
		degreelist = degreeindex.find('div', id='panel-d21e114')
		try:
			degreelist.extend(degreeindex.find('div', id='panel-d21e1219'))
		except:
			pass
		# find every anchor tag's href (link) within the degree program list
		degreelinks = [_url_root + anchortag['href'] for anchortag in degreelist.find_all('a')]
		# download every linked page in the degree program list - presumably, degree pages, but not always
		degreepages = [bs.BeautifulSoup(requests.get(degreelink).text, 'lxml') for degreelink in degreelinks]
		for degreelink, degreepage in zip(degreelinks, degreepages):
			degrees = degrees + _accordions_to_degrees(degreelink, degreepage)
		# remove found degrees' links from degree links
		notdegreelinks = [degreelink for degreelink in degreelinks if degreelink not in [degree.id for degree in degrees] else None]
		notdegreelinks = *filter(lambda degreelink: degreelink is not None, degreelinks)
		# try to find valid degrees in the remaining invalid pages
		for notdegreelink in degreelinks:
			# all these pages should already be downloaded, so find it
			notdegreepage = degreepages[index for index,degreelink in enumerate(degreelinks) if notdegreelink is degreelink]
			# find the main content of the non-degree page
			notdegreepage_content = notdegreepage.find('div', 'col-lg-8 mb-5')
			# find all the anchor tags (links) in the non-degree page
			notdegreepage_content_links = [anchortag['href'] for anchortag in notdegreepage_content.find_all('a')]
			# test each link to see if it is a degree page
			for degreelink in notdegreepage_content_links:
				# determine if degree has been found already
				degreefound = False
				try:
					# remove preceding root url if it exists
					testlink = degreelink[len(_url_root):] if degreelink[:len(_url_root)] is _url_root else degreelink
					for j in degrees:
						# if degree already exists, skip
						if testlink == j.id:
							degreefound = True
							break
				except:
					# if there was an error determining if the root url exists, check it anyway
					degreefound = True
				if degreefound:
					# check if link is valid e.g. not an index page
					if testlink[-1] != '#' and testlink[-9:-1] != 'index.php' and testlink[-10:-1] != 'index.php#' and '/catalog/current' in testlink:
						# download test page
						degreepage = bs.BeautifulSoup(requests.get(_url_root + testlink).text, 'lxml')
						degrees = degrees + _accordions_to_degrees(degreepage, _url_root + testlink)
				else:
					break
		# check for duplicate degrees by name and remove
		degreeids = [degree.id for degree in degrees]
		degrees = [degree for degree in degrees if degreeids.count(degree.id) is 1 else None]
		degrees = *filter(lambda degree: degree is not None, degree)
		# save final degree list to local cache
		cache.save(degrees, filename)
	finally:
		print('Loaded ' + str(len(degrees)) + ' degrees')
		return degrees

if __name__ == '__main__':
	print('degree.py')
