#Program program access

# DEV to-do:
# 	Fill out semesters in programs from accordions (_accordions_to_programs)
# 	Program descriptions (_accordions_to_programs)
#		Access older catalogs (see below links)

#Current:
#	https://www.atu.edu/catalog/dev/undergraduate/programs.php
#2022-2023
# https://www.atu.edu/catalog/2022-23/undergraduate/programs.php
#2019-2021 and prior
#	https://www.atu.edu/catalog/archive/undergraduate/2021/programs.php
#2016-2018
# https://www.atu.edu/catalog/archive/undergraduate/2016/live/programs.php
#Prior to 2015: pdf format

#from lib import cache, catalog

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
		self.misc = []
		self.hours = None
	def add_course(self, name, id):
		self.courses.append(name + ' ' + id)
	def add_misc(self, name):
		self.misc.append(name)
	def add_other(self, name):
		self.others.append(name)
	def set_hours(self, hours):
		self.hours = hours

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
						if course_container.find('strong').get_text() == "Total Hours":
							semester.set_hours(course_container.find_all('td')[1].find('strong').get_text())
					except AttributeError:
						course_links = course_container.find_all('a')
						for course_link in course_links:
							course_name = course_link.get_text()
							course_subject = course_name.split(' ')[0]
							course_id = course_name.split(' ')[1]
							try:
								if course_subject.upper() == course_subject and str(int(course_id)) == course_id:
									semester.add_course(course_subject, course_id)
								else:
									semester.add_misc(course_name)
							except ValueError:
								if course_id.count('X') > 2:
									semester.add_other(course_name)
								else:
									print('unsure what to do with' + course_name)

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
			program_name = programpage.find('div', 'col-lg-8 mb-5').find('h1').get_text()
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
		programs = catalog.search('name', input('Enter name of a program: '))
		print('Results:')
		program = None
		if len(programs) > 1:
			for k,v in enumerate(programs):
				print(str(k + 1) + '. ' + v.name)
			try:
				program = programs[int(input('Choose a program: ')) - 1]
			except ValueError:
				pass
		if program == None:
			print('No search results or error in input')
		else:
			print(program.name)
			print(program.id)
			for k,v in enumerate(program.semesters):
				print('Semester ' + str(k + 1) + ', ' + v.season + ' of ' + v.year + ' year (' + v.hours + ' hours)')
				print('Courses:', end=' ')
				for cr in v.courses:
					print(cr, end=', ')
				print('')
				print('Misc:', end=' ')
				for mi in v.misc:
					print(mi, end=', ')
				print('')
				print('Others:', end=' ')
				for ot in v.others:
					print(ot, end=', ')
				print('')