#!/usr/bin/python3

# Shared functions for saving/loading files

from os.path import exists, realpath, dirname, join, abspath
from os import remove, makedirs
import pickle

PATH_PARENT = join(realpath(dirname(__file__)), 'data', '')

def save(obj, filename):
	'''Save/overwrite object file given a specific filename'''
	target = join(PATH_PARENT, filename)
	folder = dirname(abspath(target))
	if not exists(folder): makedirs(folder)
	if exists(target): remove(target)
	with open(target, 'wb') as file:
		pickle.dump(obj, file)

def load(filename):
	'''Load object from filename and return itself'''
	target = join(PATH_PARENT, filename)
	if not exists(target): raise FileNotFoundError(target)
	with open(target, 'rb') as file:
		return pickle.load(file)

if __name__ == '__main__':
	print('PATH_PARENT = ' + PATH_PARENT)
