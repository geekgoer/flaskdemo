from flask import Flask
from flask import url_for
from markupsafe import escape

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def hello():
    return '<h1>欢迎来的我的 WATCHList!</h1><img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
    return f'User:{escape(name)}'

@app.route('/test')
def test_url_for():
    print(url_for("hello"))
    print(url_for("user_page",name='alex'))
    print(url_for("test_url_for",num=2233))
    return 'Test Page'