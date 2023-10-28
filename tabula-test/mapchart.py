# mapchart
# Original test script for extracting per-semester info from ATU degree plans

# Even though this is not main anymore, it is maintained as a refernce.

# known issues:
# 	Output (sem 4 and sem 8) is incomplete - modify to find beginning and end better instead of guessing

# Libraries used:
# 	requests.get - get documents from the internet
# 	pyquery - HTTP requests, HTML parsing
# 	Tabula - for PDF data table parsing (degree maps)
# 		MODIFIED to run with javaw instead of java (no pop-up window) (included)
# 	pdf2image.convert_from_bytes - convert degree map PDF to image
# 	Poppler - PDF renderer for pdf2image (included in script folder)
# 	io.BytesIO - save data files RAM
# 	os
# 	numpy - number/image manipulation, used with OpenCV
# 	cv2 - OpenCV, to identify PDF elements (corners)
# 		install as opencv-python

from requests import get
from pyquery import PyQuery as pq
import tabula_edit as tabula
from pdf2image import convert_from_bytes
from io import BytesIO
import os
import numpy as np
import cv2

CATALOG_URL = r'https://www.atu.edu/catalog/archive/descriptions/courses.php?catalog=U'
DEGREEMAP_YEARS_URL = r'https://www.atu.edu/advising/degreemaps.php'
DEGREEMAP_URL = r'https://www.atu.edu/advising/degreemaps/2021-22/ElectricalEngineering.pdf'

PATH_PARENT = os.path.realpath(os.path.dirname(__file__)) + "\\"
POPPLER_PATH = os.path.join(PATH_PARENT, r"poppler-22.04.0\Library\bin")

TABULA_DIV = 2.77650881
FIND_UP = False
FIND_DOWN = True

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

def main():
	# retrieve degree map and make sure the request went through
	degmap_http = get(DEGREEMAP_URL)
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
			
	# The following code is for line detection, stolen from nathancy @ SO
	# The for loops to find corners are my own invention, though.

	# convert to grayscale, Otsu's threshold
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

	# Detect horizontal lines
	horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (200,1))
	detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
	cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if len(cnts) == 2 else cnts[1]

	# Filter to middle part of map, find highest and lowest
	blist = filterline(cnts, [370, 1285])

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
	# the following two variables are also deprecated because this script no longer renders
	numsubj = 0
	numgen = 9
	delem = []

	for x in lists:
			y = str(x)
			if y.startswith('Semester '):
					cursem = int(x[9])
					print('Semester ' + str(cursem))
					numsubj = 0
					numgen = 0
			elif not y.startswith('Total') and y!='nan':
					if y.split()[0].isupper() and y.split()[1][0:4].isdigit():
							subj = y.split()[0][-4:]
							crn = str(y.split()[1])[0:4]
							print(subj + ' ' + crn)
							
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

if __name__ == "__main__":
	main()
	
# might integrate this into main, seems it could be more efficient/readable than my big bogus tag searching
#tags = pq(url=CATALOG_URL)
#subjects = tags('a').filter(lambda i, this: (pq(this).text().startswith('(') and pq(this).text().endswith(')'))).text().split()
#for subject in subjects:
#	print(subject)

# course_url = CATALOG_URL + "&subj=" + course