#!/usr/bin/python3

# Mapchart by Thomas Dodds
# Automatically download and display ATU degree programs as well-formatted flowcharts

# pickle: built-in Python module for serializing classes, objects etc., for storage
# requests: get documents from web
# html.parser: go through and find html elements and stuff. rip data from html
# pyflowchart: processing/creating flowchart.js code

from mapchart import subjects,catalog

def main():
	# Populate subjects index
	indexug = subjects.SubjectIndex(False)
	indexug.populate()
	
	try:
		course = indexug.find("ELEG 3103")
		print(course.name)
		print(course.desc)
		print("Prerequisites:")
		for prereq in course.prereqs:
			try:
				prereq_course = indexug.find(prereq)
				print(prereq + ": " + prereq_course.name)
			except:
				print(prereq)
	except:
		print("Couldn't find that course...")

if __name__ == "__main__":
	main()
