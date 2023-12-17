#!/usr/bin/python3

# Shared functions for saving/loading files.
# Set True to throw exceptions for file accesses:
FORCE_DISABLE_CACHE = False

from os.path import exists, realpath, dirname, join, abspath
from os import remove, makedirs
from pickle import dump, load

PATH_PARENT = join(realpath(dirname(__file__)), "")

def cache_save_auto(obj):
	'''Save/overwrite object file using object's name'''
	#Only use if classes specify their own filename
	filename = obj.filename
	cache_save(obj, filename)

def cache_save(obj, filename):
	'''Save/overwrite object file given a specific filename'''
	if FORCE_DISABLE_CACHE:
		raise Exception("FORCE_DISABLE_CACHE is set, not saving " + filename)
	print("save " + obj.__class__.__name__ + " as " + filename + "...", end=" ")
	target = join(PATH_PARENT, filename)
	folder = dirname(abspath(target))
	if not exists(folder): makedirs(folder)
	if exists(target): remove(target)
	with open(target, "wb") as file:
		# If saving raw bytes, do not pickle (e.g. pdf data)
		if(str(type(obj)) == "<class 'bytes'>"):
			file.write(obj)
		else:
			dump(obj, file)

def cache_load(filename):
	'''Load object from filename and return it as itself'''
	if FORCE_DISABLE_CACHE:
		raise Exception("FORCE_DISABLE_CACHE is set, not loading " + filename)
	target = join(PATH_PARENT, filename)
	if not exists(target): raise FileNotFoundError(target)
	with open(target, "rb") as file:
		#Try to unpickle object, return raw bytes if can't
		try:
			return load(file)
		except:
			return file.read()

if __name__ == "__main__":
	print("common.py test")
	print("PATH_PARENT = " + PATH_PARENT)
