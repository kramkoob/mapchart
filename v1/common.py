# Contains functions common to the other scripts.

# cache_save: deletes old cache file and overwrites it with a pickled object
# cache_load: checks for the file, and if it's there, load it and unpickle it

from os.path import exists
from os import remove
from pickle import dump, load

def cache_save(obj, filename):
	#print("save " + obj.__class__.__name__ + " as " + filename + "...", end=" ")
	if exists(filename):remove(filename)
	with open(filename, "wb") as file:
		dump(obj, file)
	#print("done")

def cache_load(filename):
	#print("load " + filename)
	if not exists(filename): raise FileNotFoundError(filename)
	with open(filename, "rb") as file:
		return load(file)