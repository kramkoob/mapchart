#!/usr/bin/python3

# Contains functions common to the other scripts.
# Enable FORCE_DISABLE_CACHE to disable all file access

from os.path import exists, realpath, dirname, join, abspath
from os import remove, makedirs
from pickle import dump, load

PATH_PARENT = join(realpath(dirname(__file__)), "")
FORCE_DISABLE_CACHE = False

def cache_save_auto(obj):
	'''Save/overwrite object file using object's name'''
	#Only use if classes specify their own filename
	filename = obj.filename
	cache_save(obj, filename)

def cache_save(obj, filename):
	'''Save/overwrite object file given a specific filename'''
	if FORCE_DISABLE_CACHE:
		raise Exception("FORCE_DISABLE_CACHE is set, no files saved")
	#print("save " + obj.__class__.__name__ + " as " + filename + "...", end=" ")
	target = join(PATH_PARENT, filename)
	folder = dirname(abspath(target))
	if not exists(folder): makedirs(folder)
	if exists(target): remove(target)
	with open(target, "wb") as file:
		if(str(type(obj)) == "<class 'bytes'>"):
			file.write(obj)
		else:
			dump(obj, file)
	#print("done")

def cache_load(filename):
	'''Load object from filename and return it as itself'''
	if FORCE_DISABLE_CACHE:
		raise Exception("FORCE_DISABLE_CACHE is set, no file access permitted")
	#print("load " + filename)
	target = join(PATH_PARENT, filename)
	if not exists(target): raise FileNotFoundError(target)
	with open(target, "rb") as file:
		#Auto-differentiate between pickled and raw formats
		#If unpickling fails, this will throw and fallback
		try:
			return load(file)
		except:
			return file.read()

if __name__ == "__main__":
	print("common.py test script")
	print("PATH_PARENT = " + PATH_PARENT)
