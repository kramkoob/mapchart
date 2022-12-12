# mapchart
# by Thomas Dodds

# Retrieve and conveniently display ATU degree paths

# Caching to be done ASAP... home internet is slow and this is ridiculous
# Get degree map and rip data  rewrite degree
# Get subjects as they are encountered in degree maps
# Make charts

# pickle: built-in Python module for serializing classes, objects etc., for storage
# requests: get documents from web
# html.parser: go through and find html elements and stuff. rip data from html

import subjects
import catalog

# Populate subjects index
grad_index = SubjectIndex()
grad_index.populate()

# Populate all subjects
for subject in grad_index.subjects:
	subject.populate()


# Ask user for subject or course to identify
print("Find a subject or course")
print("Enter abbreviation (ELEG) to identify a subject")
print("Enter ? to list all subjects")
print("Enter \"abbreviation ?\" to list all courses in a subject")
print("Enter \"abbreviation number\" to print details of a course")

while(True):
	query = input("> ").strip()
	if "?" in query.split(" ", 1)[0]:
		for subject in grad_index.subjects:
			if not subject.empty:
				print(subject.name + " (" + subject.prefix + "): " + str(len(subject.courses)) + " courses")
	else:
		try:
			secondq = ("?" in query.split(" ", 1)[1])
		except:
			secondq = False
		if secondq:
			result = grad_index.find(query.split(" ", 1)[0])
			for course in result.courses:
				print(course.prefix + " " + str(course.number) + ": " + course.name)
		else:
			result = grad_index.find(query)
			try:
				if "Subject" in str(type(result)):
					print(result.name + " (" + result.prefix + "): " + str(len(result.courses)) + " courses")
				else:
					print(result.prefix + " " + str(result.number) + ": " + result.name)
					print(result.desc)
			except:
				print("Didn't quite understand that...")
