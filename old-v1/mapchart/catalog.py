#!/usr/bin/python3

#Catalog data access frontend

#https://www.atu.edu/catalog/archive/app/descriptions/catalog-data.php
#	term: 202220, 200740 etc.
#	subject: ELEG, MATH, STAT, ENGL etc.
#	number: 4133, 1013 etc.
#	campus: B (All), M (Russellville), 1 (Ozark)

#from lib import cache

import requests
import bs4 as bs
from os.path import join

_E_TERMS_FAILED = 'Failed to load catalog terms. Perhaps the catalog website was updated?'

_url_endpoint = 'https://www.atu.edu/catalog/archive/app/descriptions/catalog-data.php'
_url_terms = 'https://www.atu.edu/catalog/archive/app/descriptions/index.php'

#Classes
class Term:
	def __init__(self, id, name='null'):
		self.name = name
		self.id = self._check(id)
	def _check(self, id):
		if not isinstance(id, str):
			raise Exception('got ' + str(type(id)) + ', requires <class \'str\'>')
		if int(id[:4]) < 2007:
			raise Exception('invalid term year ' + id)
		return id

class Course:
	def __init__(self):
		self.name = 'null'
		self.id = '0000'
		self.subject = Subject()
		self.desc = 'null'
	def __init__(self, name, id, subject):
		self.name = name
		self.id = self._check(id)
		self.subject = subject
		self.desc = 'null'
	def _check(self, id):
		if not isinstance(id, str):
			raise Exception('got ' + str(type(id)) + ', requires <class \'str\'>')
		if len(id) > 4:
			raise Exception('invalid course id ' + id)
		return id
	def get_desc(self, term):
		try:
			search = cache.load(join(term.id, self.subject.id, 'courses.dat'))
			for i in search:
				if i.id == self.id:
					if i.desc == 'null':
						raise Exception('null description stored in file')
					self.desc = i.desc
		except:
			endpoint = bs.BeautifulSoup(_endpoint(term=term, subject=self.subject, number=self.id), 'lxml-xml')
			self.desc = _cdata_text(endpoint.find('description').get_text())
			desc_bs = bs.BeautifulSoup(self.desc, 'lxml')
			count = 0
			for i in desc_bs.find_all('br'):
				i.extract()
			self.desc = desc_bs.get_text()
			search = cache.load(join(term.id, self.subject.id, 'courses.dat'))
			for k,v in enumerate(search):
				if v.id == self.id:
					search[k] = self
			cache.save(search, join(term.id, self.subject.id, 'courses.dat'))
		return self.desc

class Subject:
	def __init__(self, name='null', id='0000'):
		self.name = name
		self.id = self._check(id)
	def _check(self, id):
		if not isinstance(id, str):
			raise Exception('got ' + str(type(id)) + ', requires <class \'str\'>')
		if len(id) > 4:
			raise Exception('invalid subject code ' + id)
		return id

#Private methods
def _endpoint(term='', subject='', number='', campus='B'):
	request = _url_endpoint + '?campus=' + campus
	if term != '':
		if isinstance(term, str):
			request = request + '&term=' + term
		else:
			request = request + '&term=' + term.id
	if subject != '':
		if isinstance(subject, str):
			request = request + '&subject=' + subject
		else:
			request = request + '&subject=' + subject.id
	if number != '':
		request = request + '&number=' + number
	return requests.get(request).text

def _cdata_text(string):
	return string.removeprefix('<![CDATA[').removesuffix(']]').strip()

#Public methods
def terms():
	'''
	try:
		terms = cache.load('terms.dat')
	except FileNotFoundError:
		terms = list()
		termspage = requests.get(_url_terms)
		termspage_bs = bs.BeautifulSoup(termspage.text, 'lxml')
		termselect = termspage_bs.find(id='term')
		termstags = termselect.find_all('option')
		for i in termstags:
			terms.append(Term(i['value'], i.get_text()))
		cache.save(terms, 'terms.dat')
	if len(terms) == 0:
		raise Exception(_E_TERMS_FAILED)
	'''
	print("NOTE: The catalog access backend was broken in the recent website update. The Spring 2024 and Fall 2023 terms are the only ones manually available until a solution is found.")
	terms=[Term('202420', 'Spring 2024'), Term('202380', 'Fall 2023')]
	return terms

def subjects(term):
	filename = join(term.id, 'subjects.dat')
	try:
		subjects = cache.load(filename)
	except:
		subjects = list()
		endpoint = bs.BeautifulSoup(_endpoint(term=term), 'lxml-xml')
		subjectsxml = endpoint.find_all('subject')
		for i in subjectsxml:
			name = _cdata_text(i.find('description').get_text())
			id = i.find('code').get_text()
			subjects.append(Subject(name, id))
		cache.save(subjects, filename)
	return subjects

def courses(term, subject):
	filename = join(term.id, subject.id, 'courses.dat')
	try:
		courses = cache.load(filename)
	except:
		courses = list()
		endpoint = bs.BeautifulSoup(_endpoint(term=term, subject=subject), 'lxml-xml')
		coursesxml = endpoint.find_all('course')
		for i in coursesxml:
			name = _cdata_text(i.find('title').get_text())
			id = i.find('number').get_text()
			courses.append(Course(name, id, subject))
		cache.save(courses, filename)
	return courses

if __name__ == '__main__':
	import cache
	print('Salutations from catalog.py')
	termList = terms()
	print('ATU\'s catalog goes back ' + str(len(termList)) + ' terms')
else:
	try:
		from . import cache
	except ImportError:
		import cache