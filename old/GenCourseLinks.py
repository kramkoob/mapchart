#!/usr/bin/python3

#Mass generate links to course reference pages
#Not reliant on any custom libraries in the mapchart repository

#Links work when they want to. No further support on this script

_url_base = r'https://www.atu.edu/catalog/current/undergraduate/courses/'
_url_median = r'.php#:~:text='
_url_separate = r'%20'
_url_end = r'%3A%20'

from sys import stdin

def main():
	print('Generate course description links')
	if stdin.isatty():
		print('Provide input file via stdin')
	else:
		for k, v in enumerate(stdin, 1):
			v = v[:-1] #remove trailing endline
			subject = v.split(' ')[0].lower()
			course = v.split(' ')[1].lower()
			url = _url_base
			url = url + subject
			url = url + _url_median
			url = url + subject
			url = url + _url_separate
			url = url + course
			url = url + _url_end
			print(url)

if __name__ == '__main__':
	main()
