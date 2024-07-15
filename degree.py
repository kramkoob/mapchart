#!/usr/bin/python3

#	Provides online or offline data access. Run this by itself to provide a simple interactive data browser.

#	Includes the cache and catalog files from this library.

#	ProgramCatalog is based on Catalog - see catalog.py for more info on that.
#		Included in ProgramCatalog are functions that populate itself - namely, populate()
#			Use force=True to force an online update of fresh data ans save it (unless - see below).
#			Use save=False to disallow updating the offline database.
#		Once downloaded, data is saved in the library folder at data/programs.dat by default.
#	Program is an individual program of study.
#		Attributes: name, id, semesters.
#			name is a properly formatted name, e.g. Bachelor of Science in Electrical Engineering
#     id is the URL where the program data was retrieved from.
#			semesters is a list of Semester objects - usually 8 of them.
#	Semester is a semester in a program of study.
#		Attributes: year, season, courses, others, hours
#			year is what student academic year, e.g. Freshman, Junior etc.
#			season is which half of the year - either Fall or Spring
#			courses is a list of strings (for now) of course names.
#			others is a list of other things, like "fine arts and humanities" or "SS 1XXX Social Studies" etc.
#			hours is how many hours the website gives in their tally for credit hours in the semester.

try:
	from . import cache
	from .catalog import Catalog as basecatalog
except ImportError:
	import cache
	from catalog import Catalog as basecatalog

import requests
import bs4 as bs
from os.path import join

_url_program_list = r'https://www.atu.edu/catalog/current/undergraduate/programs.php'
_url_root = r'https://www.atu.edu'

class Semester():
	def __init__(self, year, season):
		self.year = year
		self.season = season
		self.courses = []
		self.others = []
		self.electives = []
		self.hours = None
	def add_course(self, name, id):
		self.courses.append(name + ' ' + id)
	def add_other(self, name):
		if len(name): self.others.append(name)
	def add_elective(self, name):
		if len(name): self.electives.append(name)
	def set_hours(self, hours):
		hours = ''.join([ch if ch.isalnum() else '' for ch in hours])
		self.hours = int(hours[-2:])

class Program():
	def __init__(self, id, name):
		self.name = name
		self.id = id
		self.semesters = []
	def _add_semester(self, year, season):
		semester = Semester(year, season)
		self.semesters.append(semester)
		return semester
	def add_track(self, n):
		self.name = self.name + ' Track ' + str(n)
	def populate_semesters(self, accordionelement):
		# rip semesterly plan
		cards = accordionelement.find_all('div', 'card')
		for card in cards:
			year = card.find('button', 'accordion-trigger').get_text()
			tables = card.find_all('table')
			for table in tables:
				season = table.find('thead').find('th').get_text()
				semester = self._add_semester(year, season)
				course_containers = table.find_all('tr')
				course_containers.pop(0) #remove first tr (header)
				for course_container in course_containers:
					try:
						# if this row is a total hours indicator, add that number to the semester
						if course_container.find('strong').get_text() == "Total Hours":
							try:
								semester.set_hours(course_container.find_all('td')[1].find('strong').get_text())
							except ValueError:
								print(f"Warning: No hours given for {season} semester of {year} year in {self.name}")
								semester.set_hours("0")
					except AttributeError:
						# each anchor tag has info embedded w/ more catalog info (incl. prerequisites)
						course_links = course_container.find_all('a')
						for course_link in course_links:
							course_name = course_link.get_text()
							course_subject = course_name.split(' ')[0]
							course_id = course_name.split(' ')[1]
							try:
								# these anchor tags are valid courses
								if course_subject.upper() == course_subject and str(int(course_id)) == course_id:
									semester.add_course(course_subject, course_id)
								else:
									print(f"Warning: Add course failed for {course_name} {course_subject} {course_id} in {self.name}, semester {season} of {year} year, but did not throw ValueError")
							except ValueError:
								# these anchor tags are usually subject-specific electives
								if course_id.count('X') > 2:
									semester.add_other(course_name)
								else:
									print('Warning: Absolutely unsure what to do with' + course_name)
						# if there were no anchor tags, this is probably a technical/etc. elective
						if len(course_links) == 0:
							semester.add_elective(' '.join(''.join([c if (c.isalpha() or c == ' ')  else '' for c in course_container.find('td').get_text()]).split()))

class ProgramCatalog(basecatalog):
	def __init__(self):
		basecatalog.__init__(self, Program)
		self.filename = 'programs.dat'
	def _accordion_to_programs(self, programpage, programlink):
		programlist = []
		track = 0
		# find the div with accordion class
		accordionelements = programpage.find_all('div', 'accordion')
		for accordionelement in accordionelements:
			# create program
			# name found from h1 header at top of page
			program_name = ' '.join(programpage.find('div', 'col-lg-8 mb-5').find('h1').get_text().split())
			# id is the link to the program page
			program_id = programlink
			_program = Program(program_id, program_name)
			# one major has two tracks listed on the same page. append track number if that's the case.
			if len(accordionelements) > 1:
				track = track + 1
				_program.add_track(track)
			_program.populate_semesters(accordionelement)
			programlist.append(_program)
		return programlist
	def populate(self, force=False, save=True):
		try:
			if force:
				raise FileNotFoundError
			else:
				self._contents = cache.load(self.filename)
		except FileNotFoundError:
			print('Refreshing programs')
			# load programs page
			programindex = bs.BeautifulSoup(requests.get(_url_program_list).text, 'lxml')
			# find the list element on the program page
			programlist = programindex.find('div', id='panel-d21e114')
			programlist.extend(programindex.find('div', id='panel-d21e1219'))
			# find every anchor tag's href (link) within the program list
			programlinks = [_url_root + anchortag['href'] for anchortag in programlist.find_all('a')]
			# download every linked page in the program list - presumably program pages, but not always
			programpages_texts = [requests.get(programlink).text for programlink in programlinks]
			programpages = [bs.BeautifulSoup(programpage_text, 'lxml') for programpage_text in programpages_texts]
			for programlink, programpage in zip(programlinks, programpages):
				self._contents.extend(self._accordion_to_programs(programpage, programlink))
			# create list of invalid pages
			#notprogramlinks = [programlink for programlink in programlinks if programlink not in [program.id for program in self.programs]]
			notprogramlinks = [programlink for programlink in programlinks if programlink not in [program.id for program in self._contents]]
			# try to find valid programs in the remaining invalid pages
			for notprogramlink in notprogramlinks:
				# all these pages should already be downloaded, so find it
				notprogrampage = programpages[programlinks.index(notprogramlink)]
				# find the main content of the non-program page
				notprogrampage_content = notprogrampage.find('div', 'col-lg-8 mb-5')
				# find all the anchor tags (links) in the non-program page
				anchortags = notprogrampage_content.find_all('a')
				notprogrampage_links = []
				for anchortag in anchortags:
					try:
						anchortag_href = anchortag['href']
						# limit a little bit to what 
						if "#" not in anchortag_href and "catalog/" in anchortag_href:
							notprogrampage_links.append(anchortag_href)
					except KeyError:
						pass
				#	test each link to see if it is a program page
				for programlink in notprogrampage_links:
					testlink = _url_root + (programlink[len(_url_root):] if _url_root in programlink else programlink)
					# if program has not been found already, evaluate
					if testlink not in [program.id for program in self._contents]:
						# download test page
						programpage_text = requests.get(testlink).text
						programpage = bs.BeautifulSoup(programpage_text, 'lxml')
						# test if a program exists in that page
						self._contents.extend(self._accordion_to_programs(programpage, testlink))
					else:
						break
			# remove duplicates by link/id and name
			k = 0
			while k < len(self._contents):
				if ([program.id for program in self._contents].count(self._contents[k].id) > 1 and 'Track' not in self._contents[k].id) or [program.name for program in self._contents].count(self._contents[k].name) > 1:
					del self._contents[k]
					k -= 1
				k += 1
			# save final list to local cache
			if save:
				cache.save(self._contents, self.filename)
			else:
				print('Warning: Downloaded fresh data but did not save.')
		print('Loaded ' + str(len(self._contents)) + ' programs')

if __name__ == '__main__':
	print('program.py manager')
	catalog = ProgramCatalog()
	
	choice = str(input('force refresh? y/n: ')).lower()
	if choice == 'y':
		choice = str(input('save locally? y/n: ')).lower()
		catalog.populate(force=True,save=choice=='y')
	else:
		catalog.populate()
	
	while(True):
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
			except:
				print('No results for your query.')
		if program != None:
			print('')
			print(f'  Title: {program.name}')
			print(f'    URL: {program.id}')
			for semNum,sem in enumerate(program.semesters, 1):
				print(f'    Semester {semNum}: {sem.season} of {sem.year} year ({sem.hours} hours)')
				if(len(sem.courses)): print(f'      {', '.join([v for v in sem.courses])}')
				if(len(sem.others)): print(f'      {'\n      '.join([v for v in sem.others])}')
				if(len(sem.electives)): print(f'      {'\n      '.join([v for v in sem.electives])}')
		print('')