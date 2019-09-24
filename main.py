# coding:UTF-8
import re
import bottle
from bottle import route,template,run , error, request, get, redirect
from collections import Counter, defaultdict
from oauth2client.client import flow_from_clientsecrets, OAuth2WebServerFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
from beaker.middleware import SessionMiddleware
import sqlite3 as lite
import math

import enchant  # a library for spell check and auto correction

CLIENT_ID = 'XXXXXXXXXXXXXXXXXXXXXXX'
PER_PAGE = 20

# A configuration for session management 
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}

app = SessionMiddleware(bottle.app(), session_opts)


# store the value of history words
words_history = defaultdict(lambda: defaultdict(int)) 
recent_keywords = defaultdict(list)

#This is the basic page 
@route('/login','GET')
def login():
	#flow_from_clientsecrets() creates a Flow object which stores all your client data
	flow = flow_from_clientsecrets("client_secrets.json",
				scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', 
				redirect_uri="http://localhost:8080/redirect")
	# It returns an authorization server URL
	uri = flow.step1_get_authorize_url()
	bottle.redirect(str(uri))

@route('/logout','GET')
def logout():
	session = request.environ.get('beaker.session')
	session.delete()
	bottle.redirect(str('/'))

@route('/')
def index():
	session = request.environ.get('beaker.session')
	# check if there is anyone signed in
	if 'email' in session:
		user_mail = session['email']
	#	user_pic  = session['picture']
		user_name = session['name']
		loggedin = True
		return template("index.html", results = "" , history = "" , recent = "", loggedin = loggedin, user_mail = user_mail, user_name = user_name)

	else:
		loggedin = False
		return template("index.html", results = "" , history = "" , recent = "", loggedin = loggedin)
	


#redirct page
@route('/redirect')
def redirect_page():
	code = request.query.get('code', '')
	flow = OAuth2WebServerFlow(client_id= CLIENT_ID,                            	
				   client_secret= '7myUs1EDXK51oYhzMfEB0dw1',
		 		   scope="https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email",
				   redirect_uri="http://localhost:8080/redirect")
	credentials = flow.step2_exchange(code)
	token = credentials.id_token['sub']
	http = httplib2.Http()
	http = credentials.authorize(http)
	# Get user mail
	users_service = build('oauth2','v2',http = http)
	user_document = users_service.userinfo().get().execute()

	user_mail = user_document['email']
	user_pic  = user_document['picture']
	user_name = user_document['name']
	
	session = request.environ.get('beaker.session')
	session['email'] = user_mail
	session['picture'] = user_pic
	session['name'] = user_name
	session.save()
	bottle.redirect(str('/'))

#Extract the words from a text
def getWords(text):
	"""
	input: string
	return: list of words
	"""
	return re.compile('\w+').findall(text)

def displayHistory(h_dict,history):
	for index, key in enumerate(sorted(h_dict, key = h_dict.get, reverse = True)[:20]):
			history += ("<tr><td>" + str(index+1) + "</td><td>" + key + "</td><td>" + str(h_dict[key]) + "</td></tr>" ) 
	return history
	
def displayRecent(recent,user_mail):
	if len(recent_keywords[user_mail]) >= 10:
		recent_keywords[user_mail] = recent_keywords[user_mail][-10:]
	for index,item in enumerate(recent_keywords[user_mail][::-1]):
		recent += ("<tr><td>" + str(index+1) + "</td><td>" + item + "</td><tr>")	
	return recent


#Calculate the results and history words 
@route('/',method="POST")
def counter():
	global words_history
	global history
	global recent
	global loggedin
	session = request.environ.get('beaker.session')

	if 'email' in session:
		user_mail = session['email']
		user_pic  = session['picture']
		user_name = session['name']
		loggedin = True
	else:
		loggedin = False
		user_mail = ''
		user_pic = ''
		user_name = ''

	

	# the html code of history page
	history = """<table id="history">
			<tr><th>Rank</th><th>History</th><th>Count</th></tr>
			<caption>Top20 keywords in History</caption> """
	recent = """<table id="recent">
			  <tr><th>Rank</th><th>Recent Keywords</th></tr><caption>Recent 10 Keywords</caption>
				"""

	# get the input from the search box
	keywords = request.forms.get("keywords") 
	# return the list of words from input
	words = getWords(keywords)  

	if(len(words) <= 1):
		#update the word's frequency in the dict
		words_history[user_mail][words[0]] += 1
		recent_keywords[user_mail].append(words[0])
		#return the word
		results = """<p id="results">The Search Keyword is <b><u>""" + words[0] + "</u></b></p>"  
		history = displayHistory(words_history[user_mail],history)
		recent = displayRecent(recent, user_mail)
		
		redirect("/search/&keyword=" +  words[0] + "&page_no=1" )


		return template("index.html", results = results, history = history, recent = recent, loggedin = loggedin, user_mail = user_mail, user_name = user_name)
	else:
		#return a dict of word frequency
		words_dict = Counter(words) 
		recent_keywords[user_mail] = recent_keywords[user_mail] + words
		# the html code of results page
		results = """<table id="results"><tr><th>Rank</th><th>Word</th><th>Count</th></tr><caption>"""+ "Search for \"" + ' '.join(words) + "\"" + "</caption>"  
		for index,key in enumerate(sorted(words_dict, key = words_dict.get, reverse = True)):  # for 
			results += ("<tr><td>" + str(index+1) + "</td><td>" + key + "</td><td>" + str(words_dict[key]) + "</td></tr>" ) 
			words_history[user_mail][key] += words_dict[key]
	
		history = displayHistory(words_history[user_mail],history)
		recent = displayRecent(recent, user_mail)
		
	redirect("/search/&keyword=" +  words[0] + "&page_no=1" )

	if loggedin == True:
		
		return template("index.html",results = results, history = history, recent = recent, loggedin = loggedin, user_mail = user_mail, user_name = user_name)
	else:
		return template("index.html", results = results, history = history, recent = recent, loggedin = loggedin)


cache = defaultdict()
@route('/search/&keyword=<keyword>&page_no=<page_no>')
def search(keyword,page_no):
	# word spell correction
	d = enchant.Dict("en_us")
	if not d.check(keyword):
		d.suggest(keyword)[0]
		correction = "Do you mean <b><u>" + keyword + "</u><b>"
	else:
		correction = ""

		
	page_no = int(page_no)
	global cache	
	page_table = """<table id="page_table">
			<tr><th>Rank</th><th>Result</th>"""
	if keyword not in cache:
		con = lite.connect("links.db")
		cur = con.cursor()
		cur.execute("""SELECT DISTINCT document.link FROM lexicon, document, inv_idx, relation, score 
						WHERE lexicon.word LIKE ? AND lexicon.word_idx = inv_idx.word_idx AND document.doc_idx = inv_idx.doc_idx 
						AND inv_idx.doc_idx = score.doc_idx ORDER BY score.rank DESC;""" , (keyword,))
		results = cur.fetchall()
		con.close()
	else:
		results = cache[keyword]


	cache[keyword] = results 
	
	result_num = len(results)
	pages = result_num // PER_PAGE if result_num % PER_PAGE == 0 else result_num // PER_PAGE + 1 
	start = (page_no - 1) * PER_PAGE 
	end = page_no * PER_PAGE 

	if start > result_num:
		return error404(404)
	if end  > result_num:
		end = result_num
	
	results = results[start:end]
	
	for rank, item in enumerate(results):
		url = str(item).split("'")
		page_table += '<tr><td>' + str(rank + 1) + '</td><td><a href="' + url[1] + '" target="_blank">'+ url[1] + "</a></td></tr>"


	
	index_table = """<div class="index_table"><p>There are in total\t""" + str(result_num) +  "\tresults\n</p>"  + "To go to other pages:\n"+"""<table><tr>"""
	for i in range(1, pages + 1):
		if page_no == i:
			index_table += '<th><a href= "' + '/search/&keyword=' + keyword + '&page_no=' + str(i) + '"><b>' + str(i) + "</b><a></th>"
		else:
			index_table += '<th><a href= "' + '/search/&keyword=' + keyword + '&page_no=' + str(i) + '">' + str(i) + "<a></th>"
		

	index_table += "</tr></div>"
	return template("search.html", page_table = page_table, index_table = index_table , correction = correction)

@error(404)
def error404(error):
	message = """404 Here, please return to <a href="/">Home<a>"""
	return message
run(app = app, host = "localhost", port = 8080)
