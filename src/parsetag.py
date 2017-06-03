
import xml.sax


class parseTagHandler(xml.sax.ContentHandler):

	def __init__(self, output):
		self.output = output
		self.tag = ""
		self.attributes = {}

	def startElement(self, tag, attributes):
		for attName in attributes.getNames():
			self.attributes[attName] = attributes.getValue(attName)

	def endElement(self, tag):
		self.tag = tag
	
	def endDocument(self):
		self.output[0] = self.tag
		self.output[1] = self.attributes


def parseTag(innerString):
	'''
	A function for parsing a specific set of tags.
	Takes the contents of a tag (all text between a pair of < > brackets), and checks 
	 that the tag is valid.
	Returns the type(see below), tagname, and attributes.
	Tag type refers to if the tag is an opening tag, a closing tag, an atomic tag (one
	 that both opens and closes with one tag, like <br/>), or invalid.
	tagType values: 0 invalid, 1 opening, 2 closing, 3 atomic (binary indicates presence of tags)
	'''

	# Serves as a pointer to be passed to the sax parser.
	# output[0] is the tagname, output[1] is a dictionary of tag attributes
	output = [None, None]

	# Check if closing tag
	if innerString[0] == "/":
		tagType = 2
		tagString = "<"+innerString[1:]+"/>"

	# Check if atomic tag
	elif innerString[-1] == "/":
		tagType = 3
		tagString = "<"+innerString+">"

	# Check if opening tag
	else:
		tagType = 1
		tagString = "<"+innerString+"/>"

	# Parse tag
	try:
		xml.sax.parseString(tagString, parseTagHandler(output))
	except:
		tagType = 0

	# Return results
	return tagType, output[0], output[1]


