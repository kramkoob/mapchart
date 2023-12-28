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

_url_endpoint = 'https://www.atu.edu/catalog/archive/app/descriptions/catalog-data.php'
_url_terms = 'https://www.atu.edu/catalog/archive/app/descriptions/index.php'

class Catalog:
	class MismatchError(Exception):
		def __init__(self, got, want):
			self.message = 'got \'' + type(got).__name__ + '\' expected \'' + str(want) +'\''
		def __str__(self):
			return self.message
	class SearchTypeNotImplementedError(Exception):
		pass
	def __init__(self, obj):
		self._contents = []
		self._type = obj.__name__
	def append(self, obj):
		if type(obj).__name__ != self._type:
			raise self.MismatchError(obj, self._type)
		self._contents.append(obj)
	def search(self, aspect, query, multi='true'):
		result = []
		for item in self._contents:
			test = getattr(item, aspect)
			match type(query).__name__:
				case 'bool' | 'int':
					if query == test:
						result.append(item)
				case 'str':
					if query.lower() in test.lower():
						result.append(item)
				case _:
					raise self.SearchTypeNotImplementedError(type(query).__name__)
		try:
			return result if multi else result[0]
		except IndexError:
			return None
		
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
	def __init__(self, name, id):
		self.name = name
		self.id = self._check(id)
		self.desc = ''
	def _check(self, id):
		if not isinstance(id, str):
			raise Exception('got ' + str(type(id)) + ', requires <class \'str\'>')
		if len(id) != 4:
			raise Exception('invalid course id ' + id)
		return id

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
	

if __name__ == '__main__':
	print('testing catalog.py, see script for routine')
	
	class foo:
		def __init__(self, name):
			self.name = name
			self.isPerson = True
		def speak(self):
			print('foo.speak called on ' + self.name)
		pass
		
	catalog = Catalog(foo)
	
	newfoo  = foo('jason')
	catalog.append(newfoo)
	
	newfoo = foo('alex')
	catalog.append(newfoo)
	
	speakfoo = catalog.search('name', 'al', multi=False)
	speakfoo.speak()
	
	print('number of isPerson (should be 2): ', end='')
	print(len(catalog.search('isPerson', True)))
	
	class bar:
		pass
	newbar = bar()
	print('attempt to add different class (should fail):', end=' ')
	try:
		catalog.append(newbar)
	except Catalog.MismatchError:
		print('task failed successfully')
else:
	try:
		from . import cache
	except ImportError:
		import cache