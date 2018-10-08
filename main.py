# coding:UTF-8
import re
import bottle
from bottle import route,template,run , error, request
from collections import Counter, defaultdict


# store the value of history words
words_history = defaultdict(int) 
	
#This is the basic page 
@route('/')
def index():
	return template("index.html", results = "" , history = "")

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
	# the html code of history page
	history = """<table id="history">
			<tr><th>Rank</th><th>History</th><th>Count</th></tr>
			<caption>Top20 keywords in History</caption> """
	# get the input from the search box
	keywords = request.forms.get("keywords") 
	# return the list of words from input
	words = getWords(keywords)  

	if(len(words) <= 1):
		#update the word's frequency in the dict
		words_history[words[0]] += 1
		#return the word
		results = """<p id="results">The Search Keyword is <b><u>""" + words[0] + "</u></b></p>"  
		history = displayHistory(words_history,history)
		return template("index.html", results = results, history = history)
	else:
		#return a dict of word frequency
		words_dict = Counter(words) 
		# the html code of results page
		results = """<table id="results"><tr><th>Rank</th><th>Word</th><th>Count</th></tr><caption>"""+ "Search for \"" + ' '.join(words) + "\"" + "</caption>"  
		for index,key in enumerate(sorted(words_dict, key = words_dict.get, reverse = True)):  # for 
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
