import bottle
from bottle import route,template,run

@route('/hello')
def hello():
	return 'Hello World!'

@route('/')
def index():
	return template("index.html")


if __name__ == '__main__':
	run(host = "localhost", port = 8080, debug = True)
