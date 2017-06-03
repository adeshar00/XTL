
from parsetag import *
from text import *


# Xtl class
#{{{
class Xtl(object):
	'''
	Stores XTL text.  Besides the parse function, this is basically just a wrapper
	for Text, making it read-only.
	'''

	def __init__(self, text):
		self.__text = Text()
		self.__text.appendText(text)
	
	def __iter__(self):
		def gen():
			for c in self.__text:
				yield c
		return gen()
	
	def toText(self):
		t = Text()
		t.append(self.__text)
		return t

	def parse(self, dictStack, elementDict, mainList=None):
		'''
		TODO comment, talk about how 4 states (inEle X inTag), tag func dict, etc
		Mention that it takes arbitrary tags; ones used are defined by compiler, so could
		be switched up by calling compile function
		Parses xtl tags, and ignores all else (even if a tag)
		'''

		# TODO make a whitespace argument, for the number of tabs/spaces to be inserted before
		#  each \n?

		# TODO better comments
		# TAG VARS
		tagText = Text()
		maxTagLength = 1024*1024 # TODO magic number, FIXME
		# TODO test with this as 20, and throw a long tag in to be sure it ignores it

		# Text object returned on function termination
		returnText = Text()

		# If in the middle of an element
		inEle = False
		eleText = Text()
		eleAttributesPointer = [{}]
		eleStackSize = 0
		eleNamePointer = [""]

		# Which Text object parse results should be diverted to: depends on value of "inEle"
		currentText = {True: eleText, False: returnText}
								
		# Tuple of pointers to be passed to closetag functions
		closePointers = (dictStack, elementDict, mainList, 
		                  eleText, eleAttributesPointer, eleNamePointer, returnText)

		# Parse xtl
		for c in self:
			'''
			Buffers text until a '>' character is encountered, then takes the text between it
			and the most recent '>' to determine if a tag in the elementDict has been encountered.
			'''

			# Check if the end of a tag is potentially found
			if c != ">":
				# If not, append to tagText
				if c == "<":
					# And flush tagText in a new '<' is encountered TODO these are confusing
					currentText[inEle].appendText(tagText)
					tagText.clear()
				tagText.append(c)
				continue

			# Check that '>' is preceeded by a '<'
			if tagText.get(0) != "<":
				currentText[inEle].appendText(tagText)
				tagText.clear()
				currentText[inEle].append(">")
				continue

			# Check if tag is valid, and is one of the xtl tag types defined in elementDict
			tagString = tagText.toString(maxTagLength)
			if tagString != False:
				tagType, tagName, tagAttributes = parseTag(tagString[1:])
			if tagString==False or tagType==0 or tagName not in elementDict:
				currentText[inEle].appendText(tagText)
				tagText.clear()
				currentText[inEle].append(">")
				continue

			# Process xtl tag
			if inEle:
				# If waiting for a closing tag, check to see if this tag is it
				if tagName == eleNamePointer[0]:
					if tagType&1:
						eleStackSize+=1
					if tagType&2:
						eleStackSize-=1
					if eleStackSize<0:
						# Closing tag found: run closing script
						elementDict[eleNamePointer[0]](closePointers)
						inEle = False
					else:
						# Not it; ignore and continue
						eleText.appendText(tagText)
						eleText.append(">")
						tagText.clear()
				else:
					# Not it; ignore and continue
					eleText.appendText(tagText)
					eleText.append(">")
					tagText.clear()
			else:
				# Check if tag is an opening tag (or atomic)
				if tagType&1:
					inEle = True
					eleNamePointer[0] = tagName
					eleText.clear()
					eleStackSize = 0
					eleAttributesPointer[0] = tagAttributes
				else:
					# Closing tag encountered without a corresponding opening tag
					error = "Mismatched xtl tags, encountered closing \""
					error+= tagName
					error+= "\" tag without matching opening tag"
					raise ValueError(error)
				# Check if tag is atomic; run close script if so
				if tagType&2:
					inEle = False
					elementDict[tagName](closePointers)

			# Clear tagText
			tagText.clear()
			

		# Append remaining tagText to returnText
		returnText.appendText(tagText)

		# Check if there's an unclosed opening tag
		if inEle:
			# TODO  search all ValueErrors in this file and reevaluate
			error = "Mismatched xtl tags, a \""+eleNamePointer[0]+"\" tag was unclosed"
			raise ValueError(error)

		# Done
		return returnText

#}}}

# Xtl constructors
#{{{
def xtlFromFile(filePath):
	t = Text()
	t.appendFile(filePath)
	# TODO try file open, catch if fails and give message?
	return Xtl(t)


def xtlFromString(string):
	t = Text()
	t.append(string)
	return Xtl(t)

#}}}
