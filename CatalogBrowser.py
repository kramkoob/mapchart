#!/usr/bin/python3

#Simple catalog term/subject/course browser

from lib import catalog
from lib.interactive import test_id

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
