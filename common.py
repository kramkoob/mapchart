# Contains functions common to the other scripts.
# Enable FORCE_DISABLE_CACHE to disable all file access

from os.path import exists, realpath, dirname, join
from os import remove, mkdir
from pickle import dump, load

PATH_PARENT = join(realpath(dirname(__file__)), "")
FORCE_DISABLE_CACHE = False

def cache_library(path):
	'''Automatically tree to desired path if folders do not exist'''
	if FORCE_DISABLE_CACHE:
		raise Exception("FORCE_DISABLE_CACHE is set, no folders created")
	split = path.split("\\")
	check = PATH_PARENT
	for name in split:
		check = join(check, name)
		if not exists(check) and not FORCE_DISABLE_CACHE:
			#print("creating '%s'" % check)
			mkdir(check)

def cache_save_auto(obj):
	'''Save/overwrite object file using object's name'''
	filename = obj.filename
	cache_save(obj, filename)

def cache_save(obj, filename):
	'''Save/overwrite object file given a filename'''
	if FORCE_DISABLE_CACHE:
		raise Exception("FORCE_DISABLE_CACHE is set, no files saved")
	#print("save " + obj.__class__.__name__ + " as " + filename + "...", end=" ")
	cache_library(filename[0:filename.rindex("\\")])
	if exists(PATH_PARENT + filename): remove(PATH_PARENT + filename)
	with open(PATH_PARENT + filename, "wb") as file:
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
	if not exists(PATH_PARENT + filename): raise FileNotFoundError(PATH_PARENT + filename)
	with open(PATH_PARENT + filename, "rb") as file:
		try:
			return load(file)
		except:
			return file.read()

if __name__ == "__main__":
	print("PATH_PARENT = " + PATH_PARENT)
