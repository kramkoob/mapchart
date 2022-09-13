# done Get catalog years https://www.atu.edu/advising/degreemaps.php
# done Get list of degree maps for catalog years https://www.atu.edu/advising/degreemaps-21-22.php
# Get degree map and rip data
# Get subjects as they are encountered in degree maps
# Make charts

# pickle: built-in Python module for serializing classes, objects etc., for storage
# requests: get documents from web
# html.parser: go through and find html elements and stuff. rip data from html
# os: pause

import requests
from html.parser import HTMLParser as hp

from pyquery import PyQuery as pq
import tabula_edit as tabula
from pdf2image import convert_from_bytes
from io import BytesIO
import os
import numpy as np
import cv2

SITE_PREFIX = r"https://www.atu.edu"
CATALOG_YEARS_URL = r"/advising/degreemaps.php"
CATALOG_COURSES_URL = r"/catalog/current/undergraduate/courses/"
CATALOG_COURSES_URL_END = r".php"

CATALOG_URL = 'https://www.atu.edu/catalog/archive/descriptions/courses.php?catalog=U'
DEGREEMAP_YEARS_URL = 'https://www.atu.edu/advising/degreemaps.php'
DEGREEMAP_URL = 'https://www.atu.edu/advising/degreemaps/2021-22/ElectricalEngineering.pdf'
POPPLER_PATH = os.getcwd() + r"\poppler-22.04.0\Library\bin"
TABULA_DIV = 2.77650881
FIND_UP = False
FIND_DOWN = True


# BEGIN JANK
def filterline(cnts, bound):
    '''filter out given line list to only ones within bound'''
    blist = []
    for v in cnts:
        value = v.tolist()[0][0][1]
        if(value > bound[0] and value < bound[1]):
            blist.append(value)
    return blist

def findline(cnts, n, bound, dir=True):
    '''find nth line pos from bottom or top in a given lines list between bounds'''
    result = bound[int(not dir)]
    tresult = int(dir) * 10000
    blist = filterline(cnts, bound)
    for i in range(n - 1):
        for v in blist:
            if((v > result and v < tresult and dir) or (v < result and v > tresult and not dir)):
                tresult = v
        result = tresult
    return result

# retrieve degree map and make sure the request went through
degmap_http = requests.get(DEGREEMAP_URL)
if(degmap_http.status_code != 200):
    raise Exception("HTTP Error " + degmap_http.status_code + " for " + degmap_http.url)

# store pdf data of degree map
degmap = degmap_http.content
with BytesIO() as file:
    # convert pdf data to an image
    convert_from_bytes(degmap, poppler_path=POPPLER_PATH)[0].save(file, format="png")
    file.seek(0)
    # load virtual image
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), 1)
    
# The following code is for line detection, stolen from "nathancy" @ SO
# The for loops to find corners are my own invention, though.

# convert to grayscale, Otsu's threshold
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Detect horizontal lines
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (200,1))
detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

# Find the box at the top that has the major title


# Filter to middle part of map, find highest and lowest
blist = filterline(cnts, [370, 1285])
#blist = []
#for v in cnts:
#    value = v.tolist()[0][0][1]
#    if(value > 370 and value < 1285):
#        blist.append(value)
havg = sum(blist) / len(blist)
hmin = havg
hmax = havg
for v in blist:
    if(v < hmin):
        hmin = v
    if(v > hmax):
        hmax = v

# Detect vertical lines
vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,160))
detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
cnts = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

# Rip x-data from detected vertical lines
blist = []
for v in cnts:
    value = v.tolist()[0][0][0]
    blist.append(value)
# Average of two center ones
vavg = (cnts[4].tolist()[0][0][0] + cnts[5].tolist()[0][0][0]) / 2
v1min = 10000
v1max = 0
v2min = 10000
v2max = 0
# Find min and max for each column
for v in cnts:
    value = v.tolist()[0][0][0]
    if(value < v1min):
        v1min = value
    if(value > v2max):
        v2max = value
    if(value < vavg and value > v1max):
        v1max = value
    if(value > vavg and value < v2min):
        v2min = value

# Scale coordinates for Tabula, from px to "pdf distance units" or something
hmin /= TABULA_DIV
hmax /= TABULA_DIV
v1max /= TABULA_DIV
v1min /= TABULA_DIV
v2max /= TABULA_DIV
v2min /= TABULA_DIV

with BytesIO(degmap) as file:
    # Rip data from pdf
    col1 = tabula.read_pdf(file, pages=1, multiple_tables=True, lattice=True, stream=True, area=[hmin,v1min,hmax,v1max])[0]
    col2 = tabula.read_pdf(file, pages=1, multiple_tables=True, lattice=True, stream=True, area=[hmin,v2min,hmax,v2max])[0]
    # make a list of all the semester listings and course listings in this degree map
    lists = [col1.columns[0]] + col1[col1.columns[0]].tolist() + [col2.columns[0]] + col2[col2.columns[0]].tolist()

cursem = 0
# the following two variables are used for positioning each course title
numsubj = 0
numgen = 9
delem = []

#END JANK

class CatalogHTMLParse(hp):
	#This class is provided as a base for the other catalog classes since their data pages are structured almost identically. Inheritors MUST define a self.parse(self, data) method, called each time this class finds a result, and must also call CatalogHTMLParse.__init__(self, tablemode) in its own __init__ method, where tablemode is a boolean to slightly modify operation mode (for degree list pages, this should be True)
	def __init__(self, tablemode):
		hp.__init__(self)
		self.tablemode = tablemode
		self.check_text = False
		self.search_for_list = False
		self.search_for_maps = False
		self.get_text = False
		self.next_attr = ""

	def populate(self):
		self.feed(requests.get(self.url).text)
		# 1) First searches for paragraph with matching text, or for opening table
		# 2) Then searches the following lists and 3) their elements
		# 4) Create a CatalogYear for each year found
		# 5) Stop searching when reach the end of the main content or table
		
	def handle_starttag(self, tag, attrs):
		if (tag == "p" and not self.tablemode) or tag == "table": #1
			self.check_text = True
			self.search_for_list = self.search_for_list or self.tablemode
		if self.search_for_list and tag == "ul": #2
			self.search_for_maps = True
		if self.search_for_maps and tag == "a": #3
			self.get_text = True
			self.next_attr = attrs[0][1]
			
	def handle_endtag(self, tag):
		if self.search_for_list and (tag == "main" or tag == "table"):#5
			self.search_for_list = False
		if self.search_for_maps and tag == "ul": #2
			self.search_for_maps = False
		if self.get_text and tag == "a": #3
			self.get_text = False
	
	def handle_data(self, data):
		if self.check_text: #1
			self.search_for_list = data.startswith("Degree Maps by catalog year") or self.tablemode
			self.check_text = not self.search_for_list
		if self.get_text: #4
			self.parse(data, self.next_attr)

class Catalog(CatalogHTMLParse):
	# Contains each year
	def __init__(self):
		CatalogHTMLParse.__init__(self, False)
		self.catalogyears = []
		self.url = SITE_PREFIX + CATALOG_YEARS_URL
	
	def parse(self, data, attr):
		self.catalogyears.append(CatalogYear(data, attr))
    
class CatalogYear(CatalogHTMLParse):
	# Contains the degrees offered each year
	def __init__(self, year, url):
		CatalogHTMLParse.__init__(self, True)
		self.degrees = []
		
		self.year = int(year[2:4]) #takes "2021-2022" and strips to an integer 21 (in this instance)
		self.year_formatted = str(self.year) + "-" + str(self.year + 1) # "21-22"
		self.year_formatted_long = year # "2021-2022"
		# link is passed from html parser, but needs the domain in front of it since it's a local address
		self.url = SITE_PREFIX + url
		
	def parse(self, data, attr):
		self.degrees.append(Degree(data, attr))

class Degree():
	# A degree. Todo: this is where PDF parsing happens
	def __init__(self, name, url):
		self.name = name
		self.url = SITE_PREFIX + url

class SubjectIndex(hp):
        # Contains all subjects.
	def __init__(self):
		hp.__init__(self)
		self.url = SITE_PREFIX + CATALOG_COURSES_URL
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

			for ind, subject in enumerate(self.subjects):
				if subject.prefix == prefix:
					return subject.find(number)

		else:
			for ind, subject in enumerate(self.subjects):
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
				self.subjects.append(Subject(data.strip()[1:(len(data) - 1)]))
			if self.handle_course:
				self.subjects[len(self.subjects) - 1].name = data.strip()

class Subject(hp):
        # Contains courses in each subject, e.g. ELEG
	# Subjects page is quite different from the catalog. And beyond that, different years have different layouts...
	def __init__(self, prefix):
		hp.__init__(self)
		self.prefix = prefix.upper()
		self.name = ""
		self.url = SITE_PREFIX + CATALOG_COURSES_URL + prefix + CATALOG_COURSES_URL_END
		self.courses = []
		
		self.search_for_data = False
		self.handle_name = False
		self.handle_course = False
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
			
	def handle_endtag(self, tag):
		self.search_for_data = (not tag == "div") and self.search_for_data
		self.handle_name = (not tag == "h1") and self.handle_name
		self.handle_course = (not tag == "h2") and self.handle_course
	
	def handle_data(self, data):
		if self.search_for_data:
			if self.handle_name:
				self.name = data
			if self.handle_course:
				course = Course(self.prefix)
				course.set_number(data.split(":", 1)[0].split(" ", 1)[1])
				course.set_name(data.split(":", 1)[1])
				self.courses.append(course)

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
				self.number = int(number[0] * 1000)
			except:
				self.number = -1
	def set_desc(self, desc):
		self.desc = descname.strip()
	def add_prereq(self, course):
		self.prereqs.append(course)
	
# Test get list of catalog years
catalog = Catalog()
catalog.populate()

# Test populating the most recent year
#for catalogyear in catalog.catalogyears:
#        catalogyear.populate()
#        print(str(len(catalogyear.degrees)) + " degrees for " + catalogyear.year_formatted_long)

# Test list all degree plans for most recent year
#for ind, degree in enumerate(catalog.catalogyears[0].degrees, start=1):
#	print(str(ind) + ") " + degree.name + " - " + degree.url + " ")

# Test populate subjects index
subjectindex = SubjectIndex()
subjectindex.populate()

# Test list all subjects
for subject in subjectindex.subjects:
	subject.populate()

# jank
for x in lists:
    y = str(x).strip()
    if y.startswith('Semester '):
        cursem = int(x[9])
        print('Semester ' + str(cursem))
        numsubj = 0
        numgen = 0
    elif not y.startswith('Total') and y!='nan':
        if y.split()[0].isupper() and y.split()[1][0:4].isdigit():
            subj = y.split()[0][-4:]
            crn = str(y.split()[1])[0:4]
            result = subjectindex.find(subj + ' ' + crn)
            if not result:
                print(subj + ' ' + crn + ": unknown " + subjectindex.find(subj).name + " course")
            else:
                print(result.prefix + " " + str(result.number) + ": " + result.name)
            
            numsubj = numsubj + 1
        else:
            
            # the ampersand is a troublesome character. add \ before it
            new_text = ''
            for character in y:
                if ord(character) == 38:
                    new_text += r"&amp;"
                else:
                    new_text += character
            
            numgen = numgen + 1
            print(y)
