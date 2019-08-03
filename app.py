# coding: utf-8
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db_session
from models import User
from celery import Celery
from celery.schedules import crontab

import os
import platform
import pyttsx3
import redis

app = Flask(__name__)
app.secret_key = 'random string'
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',

)

celery = Celery(
    app.name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'],
)
redis  = redis.Redis()
engine = pyttsx3.init()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def index():
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
            return redirect(url_for('selection'))
        else:
            flash('Wrong credentials!')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/selection', methods = ['GET'])
def selection():
    u = User.query.get(session['id'])
    return render_template('selection.html', credits=u.credits, name=u.name)

@app.route('/instructions', methods = ['POST', 'GET'])
def instructions():
    credit = request.form['credit']
    seconds = int(credit)*90
    u = User.query.get(session['id'])
    n = u.name
    u.credits -= int(credit)
    db_session.commit()
    escort_user.delay(n)
    return render_template('instructions.html', seconds=seconds, credits=u.credits)

@app.route('/logout', methods = ['POST'])
def logout():
    session.clear()
    flash('Welcome back')
    return redirect(url_for('index'))


@app.route('/test', methods = ['GET'])
def test():
    result = add_together.delay(23, 42)
    result.wait() 
    name = 'test'
    escort_user.delay(name)
    s = "Hello, " + name
    return s, 200, {'Content-Type': 'text/html; charset=utf-8'}


# Celery tasks

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1.0, incr.s(), name='increment')
    #sender.add_periodic_task(1.0, periodic.s('hello'), name='add every second')

@celery.task
def add_together(a,b):
    return a + b

@celery.task
def periodic(txt):
    return txt

@celery.task
def incr():
    showers = running_showers()
    for k,v in enumerate(showers):
        if v:
            shower = 'shower_time_sum:' + str(k+1)
            accumulated_shower_time = redis.incr(shower)
            print(shower)
            print(accumulated_shower_time)
#    return
  

# Normal functions

def running_showers():
    return redis.mget('shower1', 'shower2')

@celery.task
def escort_user(user):
    text = "Hello, " + user
    if platform.system() == 'Darwin':
        os.system("say " + text)
    else:
        engine.say("Hello, " + user)
        engine.runAndWait()
        engine.stop()
    return



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


