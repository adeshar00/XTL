
import markdown

def mdFunction(attributes, content):
	return markdown.markdown(content)

elementList=[("md", None, mdFunction)]
