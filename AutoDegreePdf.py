#!/usr/bin/python3

#AutoDegreePdf
#Generate all class pdf files given a degree
#First implementation of degree handling

from lib import catalog, degree

def main():
	print('AutoDegreePdf')
	degrees = degree.degrees(catalog.terms()[1])
	

if __name__ == '__main__':
	main()
