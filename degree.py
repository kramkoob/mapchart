#!/usr/bin/python3

#Degree program access

#Current:
#	https://www.atu.edu/catalog/dev/undergraduate/programs.php
#2022-2023
# https://www.atu.edu/catalog/2022-23/undergraduate/programs.php
#2019-2021 and prior
#	https://www.atu.edu/catalog/archive/undergraduate/2021/programs.php
#2016-2018
# https://www.atu.edu/catalog/archive/undergraduate/2016/live/programs.php
#Prior to 2015: pdf format

import cache
import catalog

import requests
import bs4 as bs
from os.path import join

_url_degree_list = 'https://www.atu.edu/catalog/current/undergraduate/programs.php'
_url_root = 'https://www.atu.edu'

class semester():
	def __init__(self, id, name):
		self.name = name
		self.id = id
		self.entries = list()
	def add_entry(self, entry):
		if isinstance(entry, catalog.course):
			self.entries.append(entry)

class degree():
	def __init__(self, id, name, term):
		self.name = name
		self.id = id
		self.term = term
		self.semesters = list()
	def add_semester(self, name):
		self.semesters.append(semester(len(self.semesters) + 1, name))

def degrees(term):
	#filename = join(term.id, 'degrees.dat')
	print("we started here")
	try:
		print('we\'re here')
		degrees = caache.load(filename)
	except:
		print("now we're here")
		degrees = list()
		degreeindex = bs.BeautifulSoup(requests.get(_url_degree_list).text, 'lxml')
		degreelist = degreeindex.find('div', id='tab-d21e100-content')
		degreeslinks = degreelist.find_all('a')
		for i in degreeslinks:
			degreepage = bs.BeautifulSoup(requests.get(_url_root + i['href']).text, 'lxml')
			print(i.get_text() + ' has ' + str(len(degreepage.find_all('div', 'accordion'))))
		
		#for i in coursesxml:
		#	name = _cdata_text(i.find('title').get_text())
		#	id = i.find('number').get_text()
		#	courses.append(course(name, id, subject))
		#cache.save(degrees, filename)
	finally:
		return degrees

if __name__ == '__main__':
	print('degree.py')
	degrees = degrees(catalog.term('202370'))