# Mapchart by Thomas Dodds
# Automatically download and display ATU degree programs as well-formatted flowcharts

# pickle: built-in Python module for serializing classes, objects etc., for storage
# requests: get documents from web
# html.parser: go through and find html elements and stuff. rip data from html

import subjects
import catalog

def main():
	# Populate subjects index
	indexug = subjects.SubjectIndex(False)
	indexug.populate()
	indexg = subjects.SubjectIndex(True)
	indexg.populate()
	
	# Populate degree index
	catalogindex = catalog.Catalog()
	catalogindex.populate()

if __name__ == "__main__":
	main()