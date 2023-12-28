#!/usr/bin/python3

# Contains all related to subjects and courses.

import requests
from html.parser import HTMLParser as hp
import common
from os.path import join

DATA_PREFIX = join("data", "")
SITE_PREFIX = r"https://www.atu.edu/catalog/current/"
SITE_CATALOG2 =r"/courses/"
SITE_COURSE_EXT = r".php"

def courselevel(number):
	'''Returns naming of a given course difficulty'''
	check = int((number - number % 1000) / 1000)
	levels = {
		1: "Freshman",
		2: "Sophomore",
		3: "Junior",
		4: "Senior",
		5: "Graduate 1st year",
		6: "Graduate 2nd year"
	}
	
	return levels.get(check, "Unknown")

class SubjectIndex(hp):
	'''Index class for all subjects. Separate for graduate and undergraduate'''
	#Inherits from HTMLParser to sift through the website code
	def __init__(self, grad=False):
		'''Initialize. Pass "true" for graduate course index'''
		hp.__init__(self)
		self.grad = grad
		self.name = "graduate" if grad else "undergraduate"
		self.url = SITE_PREFIX + self.name + SITE_CATALOG2
		self.filename = join(DATA_PREFIX, self.name + ".dat")
		self.subjects = []
		
		self.in_table = False
		self.in_row = False
		self.handle_prefix = False
		self.handle_course = False
		self.get_data = False

	def find(self, query):
		'''Search for a subject or class within the index'''
		#This stands to be optimized and made more reliable
		query = query.upper()
		if " " in query:
			#Space indicates a class e.g. ELEG 4122
			query_split = query.split(" ", 1)
			prefix = query_split[0]
			number = int(query_split[1])

			for subject in self.subjects:
				if subject.prefix == prefix:
					#Perform a search in that subject class once matching
					return subject.find(number)

		else:
			#No space indicates to simply return a subject e.g. ELEG
			for subject in self.subjects:
				if subject.prefix == query:
					return subject
	
	def fetch(self):
		'''Download and save fresh data from ATU servers'''
		#The following line is a call to HTMLParser. See the handle_* functions.
		self.feed(requests.get(self.url).text)
		#Auto-populate all subjects downloaded.
		for subject in self.subjects:
			subject.populate()
		#Attempt to save as a file unless it is not possible
		try:
			common.cache_save(self, self.filename)
		except:
			print("Unable to save cache")
	
	def populate(self):
		'''Load cached/download fresh data'''
		try:
			self.subjects = common.cache_load(self.filename).subjects
			self.subjects[0].name # if this throws then data is invalid
			return True
		except:
			self.subjects = []
			self.fetch()
			print("%u subjects for '%s'" % (len(self.subjects), self.name))
			return False
				
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
	'''Subject e.g. ELEG (and all classes therein), part of a SubjectIndex'''
	#Subject contains no means of saving as they're all part of a subject index
	def __init__(self, prefix, grad):
		hp.__init__(self)
		self.prefix = prefix.upper()
		self.grad = grad
		self.grad_url = "graduate" if grad else "undergraduate"
		self.name = ""
		self.url = SITE_PREFIX + self.grad_url + SITE_CATALOG2 + self.prefix + SITE_COURSE_EXT
		self.courses = []
		
		self.search_for_data = False
		self.handle_name = False
		self.handle_course = False
		self.handle_desc = False
		self.empty = False
		
	def find(self, query):
		'''Search index for a specific course number'''
		number = int(query)
		for ind, course in enumerate(self.courses):
			if course.number == number:
				return course

	def populate(self):
		'''Download data from the internet'''
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
				course.name = data.split(":", 1)[1].strip()
				self.courses.append(course)
			if self.handle_desc:
				self.courses[len(self.courses) - 1].append_desc(data)

class Course():
	'''Course e.g. ELEG 4122, part of a Subject'''
	#Note: Nearly all variables set externally
	def __init__(self, prefix):
		self.prefix = prefix

		self.prereqs = []
		self.name = ""
		self.number = 0
		self.desc = ""
		self.level = ""
		self.hours = 0
			
	def set_number(self, number):
		'''Set course number, level description and hours'''
		try:
			self.number = int(number)
		except:
			try:
				#Fix for the occasional "x000-level elective" sorta deal
				self.number = int(number[0]) * 1000
			except:
				self.number = -1
		self.level = courselevel(self.number)
		self.hours = self.number % 10
	
	def append_desc(self, desc):
		'''Set up description and prerequisites'''
		#Called from the HTML handler in Subject
		try:
			#Split like this to handle plural or singular "prerequisite"
			prereqs = desc.split("Prerequisite", 1)[1].split(": ", 1)[1]
			for prereq in prereqs.split(" and ", 1):
				self.add_prereq(prereq)
		except:
			#If given text/paragraph is not a prerequisite, add this description
			splitted = ""
			for split in desc.split("\n"):
				split_add = True
				#Filter out keywords
				try:
					split.split("Offered", 1)[1]
					split_add = False
				except: pass
				try:
					split.split("Prerequisite", 1)[1]
					split_add = False
				except: pass
				try:
					split.split("$", 1)[1]
					split_add = False
				except: pass
				#If keyword wasn't found and it has length, add
				if(split_add and len(split) > 0):
					to_split = " ".join(split.split())
					if(len(split) > 1):
						splitted += to_split
			#Go through and destroy double space instances
			splitted = " ".join(splitted.split())
			for x in splitted:
				#Make sure each character we're adding is real
				self.desc += (x if x.isalnum() or x == " " else "")
	
	def add_prereq(self, course):
		'''Append prerequisite as a string'''
		self.prereqs.append(course.upper().strip())

if __name__ == "__main__":
	raise Exception("This isn't the script you're looking for!")
