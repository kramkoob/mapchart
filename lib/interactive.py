#!/usr/bin/python3

#Assist functions for interactivity.

def test_id(database, name='query', test=''):
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
