#!/usr/bin/python3

#Create simple PDFs containing a course's information from the catalog

from lib import catalog
from lib.interactive import test_id
from sys import stdin

def main():
	print('Make course description PDFs')
	if stdin.isatty():
		print('Provide input file via stdin')
	else:
		term = catalog.terms()[1]
		subjects = catalog.subjects(term)
		print('Using term ' + term.name)
		for k, v in enumerate(stdin, 1):
			v = v[:-1] #remove trailing endline
			subject_query = v.split(' ')[0]
			course_query = v.split(' ')[1]
			try:
				subject = [i for i in subjects if i.id == subject_query][0]
			except:
				print('Error in ' + subject_query + ', skipping')
				continue
			try:
				courses = catalog.courses(term, subject)
				course = [i for i in courses if i.id == course_query][0]
			except:
				print('Error in ' + v + ', skipping')
			print(subject.name + ' ' + subject.id + ' ' + course.id + ' ' + course.name)
			print(course.get_desc(term))
	'''
	while True:
		term = test_id(terms, "catalog term")
		subjects = catalog.subjects(term)
		courses = catalog.courses(term, test_id(subjects, "subject"))
		course = test_id(courses, "course number")
		course.get_desc(term)
		print(course.subject.id + ' ' + course.id + ' ' + course.name)
		print(course.desc)
	'''

if __name__ == '__main__':
	main()
