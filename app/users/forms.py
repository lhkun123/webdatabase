from flask import Flask, render_template
from flask import request

app = Flask(__name__)


@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('login.html')
@app.route('/signin', methods=['POST'])
def signin():
    if request.form['username']=='admin' and request.form['password']=='password':
        return '<h2>hello,admin</h2>'
    return '<h2>bad username or password</h2>'

if __name__ == '__main__':
    app.run()