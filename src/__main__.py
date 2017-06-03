
import os
import sys
import importlib

from compiler import *


def main():
	

	# Process arguments
	inputList = []
	outputDirName = "out"
	# TODO use getopt here? or don't bother?
	addonNameList = []
	args = sys.argv[1:]
	i = 0
	while i < len(args):
		if args[i]== "-o" and i+1 < len(args):
			outputDirName = args[i+1]
			i+=1
		elif args[i][:2] == "-l":
			addonNameList.append(args[i][2:])
		else:
			inputList.append(args[i])
		i+=1

	# Make output directory (raise error if it already exists)
	# TODO make it so if -o not declared, don't create a folder (and if filewrite's are attempted, raise error then), so that if someone wants to use compiler to pipe to stdout they can do so without worrying about directories
	if os.path.exists(outputDirName):
		error = "Directory "+outputDirName+" already exists."
		raise ValueError(error)

	# Generate list of absolute file paths from argument files and directories
	filePathSet = set()
	for inputString in inputList:
		
		# If arg is a filepath, append it
		if os.path.isfile(inputString):
			filePathSet.add(os.path.abspath(inputString))
			continue

		# Arg should be a directory if not a filepath: raise error if it isn't
		if not os.path.isdir(inputString):
			error = inputString+" is neither a file or a directory."
			raise ValueError(error)

		# Walk input directory to generate list of filepaths
		for inroot, dirs, files in os.walk(os.path.abspath(inputString)):
			for fileName in files:
				# Skip hidden files
				if fileName[0] == ".":
					continue
				# Add path to list
				filePathSet.add(inroot+"/"+fileName)
	

	# Make sure list of file paths is non-empty
	if len(filePathSet)<1:
		raise ValueError("No input files or directories.")

	# Generate addon list from addon names
	addonList = []
	for addonName in addonNameList:
		''' TODO delete
		if not os.path.isfile(addon):
			raise ValueError("Addon "+addon+" not found in \"addons\" directory.")
		'''
		addonList.append(importlib.import_module("addons."+addonName))
		
	# Make output directory and change working directory to it
	os.makedirs(outputDirName)
	os.chdir(outputDirName)

	# Compile files
	compileXtl(list(filePathSet), addonList)


if __name__ == "__main__":
	main()
