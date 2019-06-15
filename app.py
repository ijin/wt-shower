# coding: utf-8
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db_session
from models import User

app = Flask(__name__)
app.secret_key = 'random string'

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def index():
    #return render_template('boot.html')
    #return render_template('bootstrap.html')
    return render_template('login.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        u = User.query.filter(User.email == email, User.password == password).first()
        if u:
            session['id'] = u.id
            flash('You were successfully logged in')
            return redirect(url_for('welcome'))
        else:
            flash('Wrong credentials!')
            return redirect(url_for('index'))
    else:
        return "Result: {}".format("bbb")


@app.route('/welcome', methods = ['GET'])
def welcome():
    u = User.query.get(session['id'])
    return render_template('welcome.html', credits=u.credits)

@app.route('/instructions', methods = ['POST', 'GET'])
def instructions():
    credit = request.form['credit']
    seconds = int(credit)*90
    u = User.query.get(session['id'])
    u.credits -= int(credit)
    db_session.commit()
    return render_template('instructions.html', seconds=seconds, credits=u.credits)

@app.route('/logout', methods = ['POST'])
def logout():
    session.clear()
    flash('Welcome back')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
