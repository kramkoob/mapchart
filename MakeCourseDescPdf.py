#!/usr/bin/python3

#Create simple PDFs containing a course's information from the catalog

#Library used: pdfkit (aur: python-pdfkit, which requires aur: wkhtmltopdf, which requires aur: qt5-webkit): Create PDF files from HTML templates

'''
Sample course list for Electrical Engineering:
ENGL 1013
CHEM 2124
MATH 2914
ELEG 1011
TECH 1001
ENGL 1023
COMS 1011
COMS 1013
MATH 2924
ELEG 2130
ELEG 2134
COMS 2203
PHYS 2114
PHYS 2000
MATH 3243
ELEG 2103
ELEG 3133
PHYS 2124
MATH 2934
ELEG 2111
ELEG 2113
STAT 3153
ELEG 3003
MCEG 3003
ELEG 3103
ELEG 3153
ELEG 3123
ELEG 3143
ELEG 4103
ELEG 4202
MCEG 4202
MATH 2703
ELEG 4113
ELEG 4143
ELEG 4191
ELEG 4303
ELEG 4122
ELEG 4192
'''

from lib import catalog
from lib.interactive import test_id
from sys import stdin
import os
import pdfkit
from jinja2 import Environment, FileSystemLoader

_PATH_WKHTMLTOPDF = r'/usr/bin/wkhtmltopdf'
_TEMPLATE = '''<!DOCTYPE html>
<html>
	<head lang="en">
		<meta charset="UTF-8">
		<title>{{ title }}</title>
	</head>
	<body>
		<h2>{{ title }}</h2>
		<p>{{ desc }}</p>
	</body>
</html>
'''

def main():
	print('Make course description PDFs')
	if stdin.isatty():
		print('Provide input file via stdin')
	else:
		print('Init catalog...', end=' ')
		term = catalog.terms()[1]
		subjects = catalog.subjects(term)
		print('done, using ' + term.name.upper())
		
		print('Init template... ', end=' ')
		#jenv = Environment(loader=FileSystemLoader('.'))
		#jtemp = jenv.get_template("template.html")
        jenv = Environment()
        jtemp = jenv.from_string(_TEMPLATE)
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
					'page-size': 'Letter',
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
