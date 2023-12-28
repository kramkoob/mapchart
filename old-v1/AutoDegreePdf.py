#!/usr/bin/python3

#AutoDegreePdf
#Generate all class pdf files given a degree
#First implementation of degree handling

import mapchart

def main():
	print('AutoDegreePdf')
	degrees = mapchart.degree.degrees(mapchart.catalog.terms()[1])
	

if __name__ == '__main__':
	main()
