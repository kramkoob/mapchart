#!/usr/bin/python3

#Create simple PDFs containing a course's information from the catalog

#Libraries: pdfkit, wkhtmltopdf, jinja2

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

from degree import *
from cache import PATH_PARENT

from sys import stdin
import os
import pdfkit
from jinja2 import Environment, FileSystemLoader

_PATH_WKHTMLTOPDF = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
_TEMPLATE = '''<!DOCTYPE html>
<html>
	<head lang="en">
		<meta charset="UTF-8">
		<title>{{ title }}</title>
		<meta name="pdfkit-page-size" content="A4"/>
		<meta name="pdfkit-orientation" content="Landscape"/>
		<style>
			body {
				position: relative;
				height: 100%;
			}

			div {
				margin: 0;
				position: absolute;
				top: 50%;
				transform: translateY(-50%);
			}
		</style>
	</head>
	<body>
		<div>
			<center><h1>{{ title }}</h1></center>
			<p style="font-size: 25px">{{ desc }}</p>
		</div>
	</body>
</html>
'''

def mkpdf(jtemp, name, desc, title=None):
	# file names and contents
	pfilename = f"{''.join(name.split())}.pdf"
	if title:
		pbasedir = os.path.join(PATH_PARENT, f'pdf-{name.split(' ')[0]}')
		jtemp_vars = {"title" : f'{name}: {title}', "desc" : '<br/>'.join(desc.split('\n'))}
	else:
		pbasedir = os.path.join(PATH_PARENT, 'pdf-others')
		jtemp_vars = {"title" : name, "desc" : '<br/>'.join(desc.split('\n'))}
	if not os.path.exists(os.path.join(pbasedir, pfilename)):
		# if subject has not been created, make folder
		try:
			os.makedirs(pbasedir)
		except FileExistsError:
			pass
		# create html document
		jhtml = jtemp.render(jtemp_vars)
		pconfig = pdfkit.configuration(wkhtmltopdf=_PATH_WKHTMLTOPDF)
		poptions = {
			'margin-top': '0.25in',
			'margin-right': '1.5in',
			'margin-bottom': '0.25in',
			'margin-left': '1.5in',
			'encoding': "UTF-8",
			'enable-local-file-access': None,
			'no-outline': None
		}
		# save html document as pdf
		pdfkit.from_string(jhtml, os.path.join(pbasedir, pfilename), configuration = pconfig, options = poptions)
		return 1
	else:
		# skip if file exists
		return 0

def main():
	print('Init catalog...')
	catalog = ProgramCatalog()
	catalog.populate()

	print('Init template... ', end=' ')
	#jenv = Environment(loader=FileSystemLoader('.'))
	#jtemp = jenv.get_template("template.html")
	jenv = Environment()
	jtemp = jenv.from_string(_TEMPLATE)
	print('done')

	while(True):
		# program search
		program = None
		programs = catalog.search('name', input('Search program by name, or press enter to list all: '))
		if len(programs) > 1:
			[print(f'{k}. {v.name}') for k,v in enumerate(programs, 1)]
			try:
				program = programs[int(input('Choose from the results above by its number: ')) - 1]
			except ValueError:
				print('No program selected, returning to search')
		else:
			try:
				program = programs[0]
				print(program.name)
			except IndexError:
				print('No results for your query.')
		if(program != None):
			tot = sum([len(sem.others) + len(sem.courses) for sem in program.semesters])
			print(f"{tot} PDFs to create.")
			if(input("OK to create PDFs? y/[n]: ").lower() == 'y'):
				saved = 0
				for sem in program.semesters:
					for name, title, desc, in zip(sem.courses, sem.courses_titles, sem.courses_descs):
						saved = saved + mkpdf(jtemp, name, desc, title=title)
					for name, desc in zip(sem.others, sem.others_descs):
						saved = saved + mkpdf(jtemp, name, desc)
				print(f'\r{str(saved)} PDFs saved, {str(tot - saved)} duplicates skipped.\n')

if __name__ == '__main__':
	main()
