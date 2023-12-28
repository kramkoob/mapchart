# simple program that lists and displays info about all the courses in the graduate or undergraduate catalog

# pickle: built-in Python module for serializing classes, objects etc., for storage
# requests: get documents from web
# html.parser: go through and find html elements and stuff. rip data from html

from mapchart import subjects,catalog

def main():
	# Populate subjects index
	try:
		query = input("[G]raduate or [U]ndergraduate: ").strip().upper()[0]
	except:
		print("Using undergraduate catalog")
		query = 'U'
	finally:
		index = subjects.SubjectIndex(query == 'G')
	index.populate()
	
	# Ask user for subject or course to identify
	print("Find a subject or course")
	print("Enter abbreviation (ELEG) to identify a subject")
	print("Enter ? to list all subjects")
	print("Enter \"abbreviation ?\" to list all courses in a subject")
	print("Enter \"abbreviation number\" to print details of a course")

	while(True):
		query = input("> ").strip()
		if "?" in query.split(" ", 1)[0]:
			for subject in index.subjects:
				if not subject.empty:
					print(subject.name + " (" + subject.prefix + "): " + str(len(subject.courses)) + " courses")
		else:
			try:
				secondq = ("?" in query.split(" ", 1)[1])
			except:
				secondq = False
			if secondq:
				result = index.find(query.split(" ", 1)[0])
				for course in result.courses:
					print(course.prefix + " " + str(course.number) + ": " + course.name)
			else:
				result = index.find(query)
				try:
					if "Subject" in str(type(result)):
						print(result.name + " (" + result.prefix + "): " + str(len(result.courses)) + " courses")
					else:
						print(result.prefix + " " + str(result.number) + ": " + result.name)
						print("Level: " + result.level)
						print("Hours: " + str(result.hours))
						print("Prerequisites:", end = ' ')
						for prereq in result.prereqs:
							print(prereq, end=', ')
						print()
						print(result.desc)
				except:
					print("Didn't quite understand that...")

if __name__=="__main__":
	main()
