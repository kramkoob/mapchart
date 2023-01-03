# Contains functions common to the other scripts.

# cache_save: deletes old cache file and overwrites it with a pickled object
# cache_load: checks for the file, and if it's there, load it and unpickle it

from os.path import exists, realpath, dirname, join
from os import remove, mkdir
from pickle import dump, load

PATH_PARENT = realpath(dirname(__file__)) + "\\"

def cache_library(path):
	split = path.split("\\")
	check = PATH_PARENT
	for name in split:
		check = join(check, name)
		if not exists(check):
			print("creating '%s'" % check)
			mkdir(check)

def cache_save(obj, filename):
	#print("save " + obj.__class__.__name__ + " as " + filename + "...", end=" ")
	cache_library(filename[0:filename.rindex("\\")])
	if exists(PATH_PARENT + filename): remove(PATH_PARENT + filename)
	with open(PATH_PARENT + filename, "wb") as file:
		dump(obj, file)
	#print("done")

def cache_load(filename):
	#print("load " + filename)
	if not exists(PATH_PARENT + filename): raise FileNotFoundError(PATH_PARENT + filename)
	with open(PATH_PARENT + filename, "rb") as file:
		return load(file)

if __name__ == "__main__":
	print("PATH_PARENT = " + PATH_PARENT)