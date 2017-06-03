
import tempfile


# Text class
#{{{
class Text(object):
	'''
	Class for storing potentially large strings.
	Basically just a wrapper for tempfile.SpooledTemporaryFile
	'''
	# TODO replace magic numbers in here with constants

	def __init__(self):
		self.__data = tempfile.SpooledTemporaryFile(mode = "w+", max_size=1024*1024)

	def __dump(self):
		def gen():
			chunkSize = 1024
			self.__data.seek(0)
			chunk = self.__data.read(chunkSize)
			while chunk != "":
				yield chunk
				chunk = self.__data.read(chunkSize)
		return gen()
	
	def __iter__(self):
		def gen():
			for chunk in self.__dump():
				for c in chunk:
					yield c
		return gen()

	def append(self, string):
		# TODO typecheck? search all files and do typechecking?? Or don't bother?
		# TODO rename "appendString"?
		self.__data.seek(0,2)
		self.__data.write(string)

	def appendFile(self, filePath):
		chunkSize = 1024
		self.__data.seek(0,2)
		f = open(filePath)
		chunk = f.read(chunkSize)
		while chunk != "":
			self.__data.write(chunk)
			chunk = f.read(chunkSize)

	def appendText(self, text):
		# TODO typecheck?
		for chunk in text.__dump():
			self.append(chunk)
	
	def get(self, index):
		# TODO typecheck?
		self.__data.seek(index)
		return self.__data.read(1)
	
	def clear(self):
		self.__data.seek(0)
		self.__data.truncate()
	
	def getLength(self):
		self.__data.seek(0,2)
		return self.__data.tell()

	def toFile(self, filePath):
		chunkSize = 1024
		f = open(filePath, "w")
		self.__data.seek(0)
		chunk = self.__data.read(chunkSize)
		while chunk != "":
			f.write(chunk)
			chunk = self.__data.read(chunkSize)
	
	def toString(self, maxSize):
		'''
		Returns contents of Text if under maxSize; if larger, returns false
		'''
		if self.getLength() > maxSize:
			return False
		self.__data.seek(0)
		return self.__data.read()

		
#}}}

