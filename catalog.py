#!/usr/bin/python3

# Provides organization and search functions.

# A catalog is a fancy list.
# Catalog() must be created by calling it with any object of the type the catalog expects to hold.
# Then, Catalog.append() to add objects of that type into the catalog.
#   Mismatched type will throw MismatchError.
# Then, Catalog.search() to search in the catalog.
#   First param is what aspect of the catalog contents to search.
#     So if the catalog object has obj.name, search by it using 'name'
#   Second param is what to search for.
#			We only know how to search int, bool and str types, for now.
#     If we don't know how to search for it, it'll throw SearchTypeNotImplementedError.
#   Optionally, multi=True or False.
#     If True, multiple results (if there are multiple) will be returned as a list.
#     If False, only the first result found will be returned individually.

# See the test script at the bottom for usage.

import requests
import bs4 as bs
from os.path import join

_url_endpoint = 'https://www.atu.edu/catalog/archive/app/descriptions/catalog-data.php'
_url_terms = 'https://www.atu.edu/catalog/archive/app/descriptions/index.php'

class Catalog:
	class MismatchError(Exception):
		def __init__(self, got, want):
			self.message = 'got \'' + type(got).__name__ + '\', needs to be \'' + str(want) +'\''
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
	def search(self, aspect, query, multi=True):
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
	
	print('number of entries that have isPerson (should be 2): ', end='')
	print(len(catalog.search('isPerson', True)))
	
	class bar:
		pass

	newbar = bar()
	
	print('attempt to add different class (should fail):')
	catalog.append(newbar)
	
	print('if you see this, something is wrong')
else:
	try:
		from . import cache
	except ImportError:
		import cache