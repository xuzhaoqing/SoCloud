# coding:UTF-8
import re
import bottle
from bottle import route,template,run , error, request, get
from collections import Counter, defaultdict
from oauth2client.client import flow_from_clientsecrets, OAuth2WebServerFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
from beaker.middleware import SessionMiddleware

# A configuration for session management 
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}

app = SessionMiddleware(bottle.app(), session_opts)


# store the value of history words
words_history = defaultdict(int) 
	
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
	return template("index.html", results = "" , history = "")

#redirct page
@route('/redirect')
def redirect_page():
	CLIENT_ID = '547955120410-0jk8stcsm8ddqajbfmr8rfij9obq62gk.apps.googleusercontent.com'
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
	print user_document
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



run(app = app, host = "0.0.0.0", port = 80)
