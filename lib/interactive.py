#!/usr/bin/python3

#Assist functions for interactivity.

#Search for a query in a database.
#	database: a defined list of classes that contain an id element
#	test: leave blank to prompt for input, otherwise, the id to search for
#	name: when prompting for input, the proper name of the id to search for
#
#	pressing enter at a blank input prompt will list all the possible valid input ids
#		(and corresponding names)
def test_id(database, test='', name='query'):
	while test == '':
		print('Enter ' + name + ':', end = ' ')
		test = input()
		if test == '':
			for i in database:
				print(i.id + '\t' + i.name)
	test = test.upper()
	for i in database:
		if i.id == test:
			return i
	return None
