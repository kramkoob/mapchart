#!/usr/bin/python3

#Automatically download and display ATU degree programs as well-formatted flowcharts

#Libaries used:
#	BeautifulSoup4 (python-beautifulsoup4) - HTML/XML parsing
#	lxml (python-lxml) - fast HTML/XML parser for bs4
#	requests (python-requests)- HTTP requests

from lib import catalog

def test_id(database, name):
	while True:
		test = ''
		while test == '':
			print('Enter ' + name + ':', end = ' ')
			test = input().upper()
			if test == '':
				for i in database:
					print(i.id + '\t' + i.name)
		for i in database:
			if i.id == test:
				return i

def main():
	print('Catalog Browser')
	print('At any blank prompt, hit enter to list all options')
	terms = catalog.terms()
	while True:
		term = test_id(terms, "catalog term")
		subjects = catalog.subjects(term)
		courses = catalog.courses(term, test_id(subjects, "subject"))
		course = test_id(courses, "course number")
		course.get_desc(term)
		print(course.subject.id + ' ' + course.id + ' ' + course.name)
		print(course.desc)

if __name__ == '__main__':
	main()
