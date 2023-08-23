#!/usr/bin/python3

#Create simple PDFs containing a course's information from the catalog

from lib import catalog
from lib.interactive import test_id
from sys import stdin
import os
import pdfkit
from jinja2 import Environment, FileSystemLoader

_PATH_WKHTMLTOPDF = r'/usr/bin/wkhtmltopdf'

def main():
	print('Make course description PDFs')
	if stdin.isatty():
		print('Provide input file via stdin')
	else:
		print('Init catalog...', end=' ')
		term = catalog.terms()[1]
		subjects = catalog.subjects(term)
		print('done, using ' + term.name.upper())
		
		print('Init template...', end=' ')
		jenv = Environment(loader=FileSystemLoader('.'))
		jtemp = jenv.get_template("template.html")
		print('done')

		errors = 0
		saved = 0
		skipped = 0
		
		for k, v in enumerate(stdin, 1):
			v = v[:-1] #remove trailing endline
			subject_query = v.split(' ')[0]
			course_query = v.split(' ')[1]
			try:
				subject = [i for i in subjects if i.id == subject_query][0]
			except:
				print('Error in ' + subject_query + ', skipping')
				errors = errors + 1
				continue
			try:
				courses = catalog.courses(term, subject)
				course = [i for i in courses if i.id == course_query][0]
			except:
				print('Error in ' + v + ', skipping')
				errors = errors + 1
			pbasedir = os.path.join(term.id, subject.id)
			pfilename = subject.id + course.id + r'.pdf'
			if not os.path.exists(os.path.join(pbasedir, pfilename)):
				try:
					os.makedirs(pbasedir)
				except FileExistsError:
					pass
				jtemp_vars = {"title" : subject.id + ' ' + course.id + ': ' + course.name, "desc" : course.get_desc(term)}
				jhtml = jtemp.render(jtemp_vars)
				pconfig = pdfkit.configuration(wkhtmltopdf=_PATH_WKHTMLTOPDF)
				poptions = {
					'page-size': 'A4',
					'margin-top': '0.75in',
					'margin-right': '0.75in',
					'margin-bottom': '0.75in',
					'margin-left': '0.75in',
					'encoding': "UTF-8",
					'enable-local-file-access': None,
					'no-outline': None
				}
				pdfkit.from_string(jhtml, pfilename, configuration = pconfig, options = poptions)
				os.rename(pfilename, os.path.join(pbasedir, pfilename))
				saved = saved + 1
			else:
				skipped = skipped + 1
			print('\r' + str(saved) + ' saved, ' + str(skipped) + ' skipped, ' +  str(errors) + ' errors', end='')
		print('\ncomplete')

if __name__ == '__main__':
	main()
