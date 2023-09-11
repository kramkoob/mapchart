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

def degrees(term):
	filename = join(term.id, 'degrees.dat')
	try:
		degrees = cache.load(filename)
	except:
		print('Refreshing degrees for ' + term.name + ', this may take some time...')
		degreeindex = bs.BeautifulSoup(requests.get(_url_degree_list).text, 'lxml')
		degreelist = degreeindex.find('div', id='panel-d21e114')
		try:
			degreelist.extend(degreeindex.find('div', id='panel-d21e1219'))
		except:
			pass
		degreeslinks = degreelist.find_all('a')
		degreepages = list()
		#print('beginning pass 1')
		#print('\t' + str(len(degreeslinks)) + ' candidates')
		for i in degreeslinks:
			degreelink = _url_root + i['href']
			degreepage = bs.BeautifulSoup(requests.get(degreelink).text, 'lxml')
			degreepages.append(degreepage)
		#print('\tparsing...')
		degrees = list()
		degrees_retry = list()
		for f, i in enumerate(degreepages):
			degree_bad = True
			accordions = i.find_all('div', 'accordion')
			degree_multitrack = (len(accordions) > 1)
			for k in range(len(accordions)):
				degree_bad = False
				degree_name = i.find('div', 'col-lg-8 mb-5').find('h1').get_text()
				degree_id = degreeslinks[f]['href']
				degree = Degree(degree_id, degree_name, term)
				if degree_multitrack:
					degree.add_track(k + 1)
				degrees.append(degree)
			if degree_bad:
				degrees_retry.append(degreeslinks[f]['href'])
		#print('\t' + str(len(degrees)) + ' verified')
		#print('beginning pass 2')
		#print('\t' + str(len(degrees_retry)) + ' to recheck')
		degreesfound = 0
		for i in degrees_retry:
			degreepage = bs.BeautifulSoup(requests.get(_url_root + i).text, 'lxml')
			degreepagecontent = degreepage.find('div', 'col-lg-8 mb-5')
			degreeslinks = degreepagecontent.find_all('a')
			for k in degreeslinks:
				degreefound = False
				for j in degrees:
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
				if degreefound:
					if testlink[-1] != '#' and testlink[-9:-1] != 'index.php' and testlink[-10:-1] != 'index.php#' and '/catalog/current' in testlink:
						degreelink = _url_root + testlink
						degreepagetest = bs.BeautifulSoup(requests.get(degreelink).text, 'lxml')
						accordions = degreepagetest.find_all('div', 'accordion')
						if len(accordions) > 0:
							degreefound = True
							degreesfound = degreesfound + 1
							degree = Degree(testlink, degreepagetest.find('div', 'col-lg-8 mb-5').find('h1').get_text(), term)
							degrees.append(degree)
				else:
					break
		#print('\t' + str(degreesfound) + ' rechecked valid')
		#print('beginning pass 3: remove duplicates by name')
		for deg1 in degrees:
			for k, deg2 in enumerate(degrees):
				if (deg1 is deg2) or not (deg1 in degrees) or not (deg2 in degrees):
					break
				name1 = deg1.name
				name2 = deg2.name
				if name1 == name2:
					if(deg1.id != deg2.id):
						print("*** DEGREE HAS SAME NAME AND DIFFERENT LINK ***")
						print('\tDegree: ' + name1)
						print('\tLink 1: ' + deg1.id)
						print('\tLink 2: ' + deg2.id)
					else:
						degrees.remove(deg2)
		#print('\t' + str(len(rem)) + ' duplicates removed')
		#for i in degrees:
		#	print('\t' + i.name)
		cache.save(degrees, filename)
	finally:
		print('Loaded ' + str(len(degrees)) + ' degrees')
		return degrees

if __name__ == '__main__':
	print('degree.py')
