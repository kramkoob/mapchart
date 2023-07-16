#!/usr/bin/python3

#Assist functions for interactivity.

def test_id(database, name='query', input=None):
	if input == None:
		while True:
			test = ''
			while test == '':
				print('Enter ' + name + ':', end = ' ')
				test = input().upper()
				if test == '':
					for i in database:
						print(i.id + '\t' + i.name)
	else:
		test = input.upper()
	for i in database:
		if i.id == test:
			return i
	return None
