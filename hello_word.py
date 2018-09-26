from bottle import route, run, request
import collections

@route('/')
def hello():
	return "Hello World"


@route('/search')
def search():
	return '''
		<form action ="/search" method="post">
			Search: <input name="userinput" type="text"/>
			<input value = "Search" type="submit" />
		</form>
	'''

@route('/search')
def do_search():
	userinput = request.forms.get("userinput")

	words = userinput.split(" ")
	print(words)
	wordcounter = collections.Counter(words)
	
	print(wordcounter)
	printWordCounter = """<table border = "0"><tr><th>Word</th><th>Count</th></tr>"""
	for key, value in zip(wordcounter.keys(), wordcounter.values()):
		print (key +"\t"+ str(value))
		printWordCounter += ("<tr><td>" + key + "</td><td>" + str(value) + "</td></tr>")

	print(printWordCounter)

	return "Search "+  "'%s' <br><br> %s"  %(userinput, printWordCounter) 


run(host="localhost", port="8070", debug=True)
