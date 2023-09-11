#!/usr/bin/python3

#Simple catalog term/subject/course browser

from lib import catalog
from lib.interactive import test_id

def main():
	print('Catalog Browser')
	print('At any blank prompt, hit enter to list all options')
	terms = catalog.terms()
	while True:
		term = None
		while term == None:
			term = test_id(terms, name = 'catalog term')
		subjects = catalog.subjects(term)
		subject = None
		while subject == None:
			subject = test_id(subjects, name = 'subject')
		courses = catalog.courses(term, subject)
		course = None
		while course == None:
			course = test_id(courses, name = 'course number')
		course.get_desc(term)
		print(course.subject.id + ' ' + course.id + ' ' + course.name)
		print(course.desc)

if __name__ == '__main__':
	main()
