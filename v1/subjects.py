# subjects.py

# Contains all related to subjects and courses.

#	Classes:
#		SubjectIndex
#		Subject
#		Course

import requests
from html.parser import HTMLParser as hp

SITE_PREFIX = r"https://www.atu.edu"
CATALOG_COURSES_UNDERGRAD_URL = r"/catalog/current/undergraduate/courses/"
CATALOG_COURSES_GRAD_URL = r"/catalog/current/graduate/courses/"
CATALOG_COURSES_URL_END = r".php"

class SubjectIndex(hp):
	# Contains all subjects. grad = true for grad level courses
	def __init__(self, grad=False):
		hp.__init__(self)
		self.grad = grad
		if not grad:
			self.url = SITE_PREFIX + CATALOG_COURSES_UNDERGRAD_URL
		else:
			self.url = SITE_PREFIX + CATALOG_COURSES_GRAD_URL
		self.subjects = []
		
		self.in_table = False
		self.in_row = False
		self.handle_prefix = False
		self.handle_course = False
		self.get_data = False

	def find(self, query):
		query = query.upper()
		if " " in query:
			query_split = query.split(" ", 1)
			prefix = query_split[0]
			number = int(query_split[1])

			for subject in self.subjects:
				if subject.prefix == prefix:
					return subject.find(number)

		else:
			for subject in self.subjects:
				if subject.prefix == query:
					return subject
	
	def populate(self):
		self.feed(requests.get(self.url).text)
		# 1) Search for matching div that begins this content
		# 2) Find next table row
		# 3) First data cell has abbreviation
		# 4) Second data cell has name. Return to # 2)
		# 5) Stop searching by the end of the div
		
	def handle_starttag(self, tag, attrs):
		self.in_table = (tag == "table" and attrs[1][1] == "courseList") or self.in_table
		self.in_row = (tag == "tr" or self.in_row) and self.in_table
		if(tag == "td"):
			self.handle_prefix = not self.handle_prefix
			self.handle_course = not self.handle_prefix
		self.get_data = (self.handle_prefix or self.handle_course) and tag == "a"
			
	def handle_endtag(self, tag):
		self.in_table = self.in_table and not tag == "table"
		self.in_row = self.in_row and self.in_table and not tag == "tr"
		self.handle_prefix = self.in_row and self.handle_prefix
		self.handle_course = self.in_row and self.handle_course
		self.get_data = self.get_data and not tag == "a"
	
	def handle_data(self, data):
		if self.get_data:
			if self.handle_prefix:
				self.subjects.append(Subject(data.strip()[1:(len(data) - 1)], self.grad))
			if self.handle_course:
				self.subjects[len(self.subjects) - 1].name = data.strip()

class Subject(hp):
	# Contains courses in each subject, e.g. ELEG
	# Subjects page is quite different from the catalog. And beyond that, different years have different layouts...
	def __init__(self, prefix, grad):
		hp.__init__(self)
		self.prefix = prefix.upper()
		self.grad = grad
		self.name = ""
		if not grad:
			self.url = SITE_PREFIX + CATALOG_COURSES_UNDERGRAD_URL + prefix + CATALOG_COURSES_URL_END
		else:
			self.url = SITE_PREFIX + CATALOG_COURSES_GRAD_URL + prefix + CATALOG_COURSES_URL_END
		self.courses = []
		
		self.search_for_data = False
		self.handle_name = False
		self.handle_course = False
		self.handle_desc = False
		self.empty = False
		
	def find(self, query):
		number = int(query)
		for ind, course in enumerate(self.courses):
			if course.number == number:
				return course
								
	def populate(self):
		self.feed(requests.get(self.url).text)
		# 1) Search for matching div that begins this content
		# 2) Find the large header containing the subject's actual name
		# 3) Find each medium header containing course number and name
		# 4) Parse the text data under each medium header
		# 5) Stop searching by the end of the div

		if len(self.courses) == 0:
			self.empty = True
		
	def handle_starttag(self, tag, attrs):
		self.search_for_data = (tag == "div" and attrs[0][1] == "col-lg-8 mb-5") or self.search_for_data
		self.handle_name = tag == "h1" or self.handle_name
		self.handle_course = tag == "h2" or self.handle_course
		self.handle_desc = tag == "p" or self.handle_desc
			
	def handle_endtag(self, tag):
		self.search_for_data = (not tag == "div") and self.search_for_data
		self.handle_name = (not tag == "h1") and self.handle_name
		self.handle_course = (not tag == "h2") and self.handle_course
		self.handle_desc = self.handle_desc and not tag == "p"
	
	def handle_data(self, data):
		if self.search_for_data:
			if self.handle_name:
				self.name = data
			if self.handle_course:
				course = Course(self.prefix)
				course.set_number(data.split(":", 1)[0].split(" ", 1)[1])
				course.set_name(data.split(":", 1)[1])
				self.courses.append(course)
			if self.handle_desc:
				self.courses[len(self.courses) - 1].append_desc(data)

class Course():
	# A course. Variables are set as they're come across in the course description pages. Some won't be used e.g. prereqs
	def __init__(self, prefix):
		self.prefix = prefix

		self.prereqs = []
		self.name = ""
		self.number = 0
		self.desc = ""
			
	def set_name(self, name):
		self.name = name.strip()
	def set_number(self, number):
		try:
			self.number = int(number)
		except:
			try:
				self.number = int(number[0]) * 1000
			except:
				self.number = -1
	def append_desc(self, desc):
		if len(self.desc) > 0:
			self.desc += "\n"
		self.desc += desc.strip()
	def add_prereq(self, course):
		self.prereqs.append(course)
	

