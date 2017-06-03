
from xtl import *
import os


# Compile Xtl
#{{{
def compileXtl(filePathList, addonList):
	'''
	TODO comment me!
	How this whole shibang works
	'''

	# Functions
	#{{{

	#  Process Addon
	#{{{
	def processAddon(addon, globalElementDict, mainElementDict):

		def functionGenerator(function):
			def wrapper(pointers):
				# TODO in addon documentation, note that contents shouldn't be over a gig
				dictStack     = pointers[0]
				elementDict   = pointers[1]
				contents      = pointers[3]
				attributes    = pointers[4][0]	
				returnText    = pointers[6]
				#                                       TODO replace magic number below
				innerString = Xtl(contents).parse(dictStack, elementDict).toString(1024*1024*1024)
				returnText.append(function(attributes, innerString))
			return wrapper

		# Check that addon has an elementList
		if not hasattr(addon, "elementList"):
			error = "Addon \""+addon.__name__+"\" does not contain an \"elementList\"."
			raise ValueError(error)

		for element in addon.elementList:
			if type(element) != tuple:
				error = "ElementList in addon \""+addon.__name__+"\" contains non-tuple items."
				raise ValueError(error)
			# check that tuple has 3 elements TODO
			if type(element[0]) != str:
				error = "Non-string item in first item of tuple in elementList in addon \""
				error+= addon.__name__+"\"."
				raise ValueError(error)
			# check elementname with parseelement to make sure is valid TODO
			if not callable(element[1]) and element[1]!=None:
				error = "Addon \""+addon.__name__+"\" has invalid tuple in elementList.\n"
				error = "Second item in tuple must be a callable or \"None\"."
				raise ValueError(error)
			if not callable(element[2]) and element[2]!=None:
				raise ValueError("PUT REAL ERROR HERE!!!call")
				error = "Addon \""+addon.__name__+"\" has invalid tuple in elementList.\n"
				error = "Third item in tuple must be a callable or \"None\"."
				raise ValueError(error)
			if element[0] in globalElementDict or element[0] in mainElementDict:
				error = "Error in addon \""+addon.__name__+"\":\n"
				error+= "An element with the name \""+element[0]
				error+= "\" already exists."
				raise ValueError(error)
			if callable(element[1]):
				globalElementDict[element[0]] = functionGenerator(element[1])
			else:
				globalElementDict[element[0]] = warnGlobal
			if callable(element[2]):
				mainElementDict[element[0]]   = functionGenerator(element[2])
			else:
				mainElementDict[element[0]]   = warnMain
	#}}}

	def warn(message):
		# TODO get filename, line number, and column number in here?
		print(message)

	def xs(pointers):
		dictStack     = pointers[0]
		eleText       = pointers[3]
		eleAttributes = pointers[4][0]

		if "k" not in eleAttributes:
			warn("xs element has no key: ignoring")
			return
		key = eleAttributes["k"]
		if key in dictStack[-1]:
			raise ValueError("Encountered two xs tags with key \""+key+"\".")
		dictStack[-1][key] = Xtl(eleText)


	def xpi(pointers):
		dictStack     = pointers[0]
		elementDict   = pointers[1]
		eleText       = pointers[3]
		eleAttributes = pointers[4][0]
		returnText    = pointers[6]

		#TODO check if eleText is anything other than whitespace, if so give warning?
		if "k" not in eleAttributes:
			warn("xpi element has no key: ignoring.")
			return
		key = eleAttributes["k"]
		xtl = None
		for d in dictStack[::-1]:
			if key in d:
				xtl = d[key]
		if xtl != None:
			result = xtl.parse(dictStack, elementDict)
			for c in result:
				returnText.append(c)
			#returnText.append(result.toText()) TODO cut upper two lines and uncomment this
		else:
			warn("xpi element key "+key+" has no been set: ignoring")


	def xpush(pointers):
		dictStack     = pointers[0]
		elementDict   = pointers[1]
		eleText       = pointers[3]
		returnText    = pointers[6]
		dictStack.append({})
		for c in Xtl(eleText).parse(dictStack, elementDict):
			returnText.append(c)
		dictStack.pop()


	def xout(pointers):
		dictStack     = pointers[0]
		elementDict   = pointers[1]
		eleText       = pointers[3]
		eleAttributes = pointers[4][0]

		# Print contents if no filePathKey
		if "filePathKey" not in eleAttributes:
			output = ""
			for c in Xtl(eleText).parse(dictStack, elementDict):
				output+= c
			print(output)
			return

		# Generate file from contents
		key = eleAttributes["filePathKey"]
		filePathXtl = None
		for d in dictStack[::-1]:
			if key in d:
				filePathXtl = d[key]
		if filePathXtl != None:
			filePath = filePathXtl.parse(dictStack, elementDict).toString(1024)#TODO magic number
			if os.path.isfile(filePath):
				error = "Two xout elements attempted to output file with path \""
				error+= filePath
				error+= "\""
				raise ValueError(error)
			(dirName, fileName) = os.path.split(filePath)
			if dirName!="" and not os.path.exists(dirName):
				os.makedirs(dirName)
			Xtl(eleText).parse(dictStack, elementDict).toFile(filePath)
		else:
			warn("xout element filePathKey not defined: ignoring")


	def xmain(pointers):
		mainList      = pointers[2]
		eleText       = pointers[3]
		mainList.append(Xtl(eleText))
	

	def warnGlobal(pointers):
		eleName       = pointers[5][0]
		# TODO give filename, line number, etc?
		warn("Warning: Use of a \""+eleName+"\" element outside of an xmain element has no effect.")
	

	def warnMain(pointers):
		eleName       = pointers[5][0]
		# TODO give filename, line number, etc?
		warn("Warning: Use of a \""+eleName+"\" element inside of an xmain element has no effect.")

	def xdeftag(pointers):
		'''
		dictStack     = pointers[0]
		elementDict   = pointers[1]
		mainList      = pointers[2]
		eleText       = pointers[3]
		eleAttributes = pointers[4][0]
		eleName       = pointers[5][0]
		returnText    = pointers[6]
		If custom tags can be defined and added to elementDict, a pointer to this function can
		be used as the value TODO delete this function?
		'''
		pass

	# TODO for xdeftag if going to do...
	def xcustom(pointers):
		'''
		dictStack     = pointers[0]
		elementDict   = pointers[1]
		mainList      = pointers[2]
		eleText       = pointers[3]
		eleAttributes = pointers[4][0]
		eleName       = pointers[5][0]
		returnText    = pointers[6]
		If custom tags can be defined and added to elementDict, a pointer to this function can
		be used as the value TODO delete this function?
		'''
		pass


	#}}}


	# A dictionary of xtl element names, the values being pointers to the functions
	#  that should be called when a closing tag is encountered in the parser.
	elementDict = {}

	# Stack of dictionaries of Xtls created by xs element
	xsDictStack = [{}]

	# List of Xtl objects created by xmain element
	mainList = []

	# Set element functions for global context
	globalElementDict = { "xs"   : xs   ,
	                      "xpi"  : warnGlobal,
	                      "xpush": warnGlobal,
      	                  "xmain": xmain,
      	                  "xout" : warnGlobal}

	# Set element functions for main context
	mainElementDict = { "xs"   : xs   ,
	                    "xpi"  : xpi  , 
	                    "xpush": xpush,
	                    "xmain": warnMain  ,
	                    "xout" : xout }
	
	# Process addons
	for addon in addonList:
		processAddon(addon, globalElementDict, mainElementDict)
	
	# Parse the contents of each file in file-list
	for filePath in filePathList:
		xtlFromFile(filePath).parse(xsDictStack, globalElementDict, mainList)

	# Parse the contents of the main elements from each file
	for xtl in mainList:
		xsDictStack.append({})
		xtl.parse(xsDictStack, mainElementDict)
		xsDictStack.pop()

#}}}


