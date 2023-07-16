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

from lib import cache, catalog

import requests
import bs4 as bs
from os.path import join

_url_degree_list = r'https://www.atu.edu/catalog/current/undergraduate/programs.php'
_url_root = r'https://www.atu.edu'

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
	def add_track(self, n):
		self.name = self.name + ' Track ' + str(n)

def degrees(term):
	#filename = join(term.id, 'degrees.dat')
	filename_good = join(term.id, 'degrees-good.dat')
	filename_bad = join(term.id, 'degreess-bad.dat')
	#try:
	#	degrees = cache.load(filename)
	#except:
	#	try:
	#		degreeslinks_good = cache.load(filename_good)
	#		degreeslinks_bad = cache.load(filename_bad)
	#	except:
	degreeindex = bs.BeautifulSoup(requests.get(_url_degree_list).text, 'lxml')
	degreelist = degreeindex.find('div', id='panel-d21e114')
	degreelist.extend(degreeindex.find('div', id='panel-d21e1219'))
	degreeslinks = degreelist.find_all('a')
	degreepages = list()
	print('beginning pass 1')
	print('\t' + str(len(degreeslinks)) + ' candidates')
	for i in degreeslinks:
		degreelink = _url_root + i['href']
		degreepage = bs.BeautifulSoup(requests.get(degreelink).text, 'lxml')
		degreepages.append(degreepage)
	print('\tparsing...')
	degreeslinks_good = list()
	degreeslinks_bad = list()
	for f, i in enumerate(degreepages):
		degree_bad = True
		accordions = i.find_all('div', 'accordion')
		degree_multitrack = (len(accordions) > 1)
		for k in range(len(accordions)):
			degree_bad = False
			degree_name = i.find('div', 'col-lg-8 mb-5').find('h1').get_text()
			degree_id = degreeslinks[f]['href']
			degreefind = degree(degree_id, degree_name, term)
			if degree_multitrack:
				degreefind.add_track(k + 1)
			degreeslinks_good.append(degreefind)
		if degree_bad:
			degreeslinks_bad.append(degreeslinks[f]['href'])
	print('\t' + str(len(degreeslinks_good)) + ' verified')
	print('beginning pass 2')
	print('\t' + str(len(degreeslinks_bad)) + ' to recheck')
	degreesfound = 0
	for key, i in enumerate(degreeslinks_bad):
		degreepage = bs.BeautifulSoup(requests.get(_url_root + i).text, 'lxml')
		degreepagecontent = degreepage.find('div', 'col-lg-8 mb-5')
		degreeslinks = degreepagecontent.find_all('a')
		for k in degreeslinks:
			degreefound = False
			for j in degreeslinks_good:
				try:
					if k['href'][:len(_url_root)] == _url_root:
						testlink = k['href'][len(_url_root):]
					else:
						testlink = k['href']
				except:
					degreefound = True
					break
				if testlink == j.id:
					degreefound = True
					break
			if not degreefound:
					if testlink[-1] != '#' and testlink[-9:-1] != 'index.php' and testlink[-10:-1] != 'index.php#' and 'catalog' in testlink:
						degreelink = _url_root + testlink
						degreepagetest = bs.BeautifulSoup(requests.get(degreelink).text, 'lxml')
						accordions = degreepagetest.find_all('div', 'accordion')
						if len(accordions) > 0:
							degreefound = True
							degreesfound = degreesfound + 1
							degreefind = degree(testlink, degreepagetest.find('div', 'col-lg-8 mb-5').find('h1').get_text(), term)
							degreeslinks_good.append(degreefind)
	#cache.save(degreeslinks_good, filename_good)
	#cache.save(degreeslinks_bad, filename_bad)
	#	finally:
	print('\t' + str(degreesfound) + ' rechecked valid')
	print(str(len(degreeslinks_good)) + ' total:')
	for i in degreeslinks_good:
		print('\t' + i.name)
	#finally:
	return degreeslinks_good

if __name__ == '__main__':
	print('degree.py')
	degrees = degrees(catalog.term('202370'))
