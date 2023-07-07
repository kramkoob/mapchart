#!/usr/bin/python3

# Retrieve list of terms from HTML

import requests
import bs4 as bs

_url_terms = "https://www.atu.edu/catalog/archive/app/descriptions/index.php"

class term:
	def __init__(self):
		self.name="null"
		self.id="000000"
	def __init__(self, name, id):
		self.name=name
		self.id=self._check(id)
	def _check(self, id):
		if not isinstance(id, str):
			raise Exception("got " + str(type(id)) + ", requires <class 'str'>")
		if int(id[:4]) < 2007:
			raise Exception("invalid term year " + id)
		return id

def get_terms():
	terms = list()
	termspage = requests.get(_url_terms)
	termspage_bs = bs.BeautifulSoup(termspage.text, 'html.parser')
	termselect = termspage_bs.find(id="term")
	termstags = termselect.find_all("option")
	for i in termstags:
		terms.append(term(i.get_text(), i['value']))
	return terms

def load_terms(filename):
	terms = list()
	#load
	names = list()
	ids = list()
	if not isinstance(names, list) or not isinstance(ids, list):
		raise Exception("got " + str(type(id)) + ", requires <class 'str'>")
	if not len(names) == len(ids):
		raise Exception("names/ids length mismatch: " + str(len(names)) + "/" + str(len(ids)))
	return terms

if __name__ == "__main__":
	print("Greetings from mapterms.py")
	terms = get_terms()
	for k, v in enumerate(terms):
		print(str(k) + ")\t(" + v.id + ")\t" + v.name)
