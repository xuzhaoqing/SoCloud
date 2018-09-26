# coding:UTF-8
import re
import bottle
from bottle import route,template,run , error, request
from collections import Counter, defaultdict



words_history = defaultdict(int) # store the value of history words

	
#This is the basic page 
@route('/')
def index():
	return template("index.html", results = results, history = "")

#Extract the words from a text
def getWords(text):
	"""
	input: string
	return: list of words
	"""
	return re.compile('\w+').findall(text)

def displayHistory(h_dict,history):
	for index, key in enumerate(sorted(h_dict, key = h_dict.get, reverse = True)[:20]):
			history += ("<tr><td>" + str(index+1) + "</td><td>" + key + "</td><td>" + str(words_history[key]) + "</td></tr>" ) 
	return history
	
	


#Calculate the results and history words 
@route('/',method="POST")
def counter():
	global words_history
	history = """<table id="history"><tr><th>&nbsp</th><th>History</th><tr>"""  # the html code of history page
	keywords = request.forms.get("keywords") #get the input from the search box
	words = getWords(keywords)  # return

	if(len(words) <= 1):
		words_history[words[0]] += 1
		results = """<p id="results">The Search Keyword is """ + words[0] + "</p>" 
		history = displayHistory(words_history,history)
		return template("index.html", results = results, history = history)
	else:
		words_dict = Counter(words)  #return a dict of word frequency
		
		results = """<table id="results"><tr><th>&nbsp</th><th>Word &nbsp</th><th>Count</th></tr>"""
		for index,key in enumerate(sorted(words_dict, key = words_dict.get, reverse = True)):
			results += ("<tr><td>" + str(index+1) + "</td><td>" + key + "</td><td>" + str(words_dict[key]) + "</td></tr>" )
			words_history[key] += words_dict[key]
	
		history = displayHistory(words_history,history)

		
		return template("index.html",results = results, history = history)


#@route('/', method="POST")
#def history():
	
#@error(404)
#def error404(error):
#	return template("404.html")


run(host = "localhost", port = 8080, debug = True)
