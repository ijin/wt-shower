# coding: utf-8
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_api import status 
from database import db_session
from models import User, Shower
from celery import Celery
from celery.schedules import crontab
from datetime import datetime

import os
import random
import platform
import redis
import json
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)


SHOWER_PIN_MAP = { 1:11, 2:12}

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
    credits = request.form['credit']
    user = User.query.get(session['id'])
    shower = available_shower()

    if not shower:
        return render_template('unavailable.html')
    #if not credits_available:
    #    return render_template('no_credits.html')
    else:
        assign_shower(shower, user, credits)
        seconds = int(credits)*90
        escort_user.delay(user.name, shower.id, seconds)
        return render_template('instructions.html', seconds=seconds, credits=user.credits, shower=shower.id)

# TODO: OOP
def available_shower():
    showers = Shower.query.filter_by(assigned=False).all()
    count = len(showers)
    if count == 0:
        return None
    else:
        index = random.randint(0, count-1)
        print(f"shower{index+1} available")
        return showers[index]
    
# TODO: OOP
def assign_shower(shower, user, credits):
    seconds = int(credits)*90
    user.credits -= int(credits)
    shower.assigned = True
    shower.seeconds_allocated = seconds
    db_session.commit()
    return shower

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
    escort_user.delay(name, 50, 100)
    s = "Hello, " + name
    return s, 200, {'Content-Type': 'text/html; charset=utf-8'}


# API
@app.route('/api/toggle', methods = ['POST'])
def toggle():
    try:
        j = request.get_json()
        shower_id = j['shower']
        shower_status = int(redis.get(f"shower{shower_id}") or 0)
        toggle_status = not bool(shower_status)
        GPIO.output(shower_pin(shower_id), not toggle_status) # 1 == off
        redis.set(f"shower{shower_id}", int(toggle_status))
        print(f"shower id: {shower_id}, status: {toggle_status}")
        result = {
            "shower": {
                "id": shower_id,
                "status": toggle_status
            }
        }
        return jsonify(result)
    except Exception as e:
        result = error_handler(e)
        return result, status.HTTP_500_INTERNAL_SERVER_ERROR

# test
@app.route('/api/shower_off/<shower_id>', methods = ['GET'])
def shower_off(shower_id):
    try:
        #j = request.get_json()
        #shower_id = j['shower']
        GPIO.output(shower_pin(int(shower_id)), 1)
        redis.set(f"shower{shower_id}", 0)
        return "off"
    except Exception as e:
        result = error_handler(e)
        return result, status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/api/shower_clear/<shower_id>', methods = ['GET'])
def shower_clear(shower_id):
    db_session.query(Shower).filter_by(id=shower_id).update(dict(assigned=False,started_at=None,paused_at=None,seconds_allocated=None))
    db_session.commit()
    GPIO.output(shower_pin(int(shower_id)), 1)
    redis.set(f"shower{shower_id}", 0)
    redis.set(f"shower_time_sum:{shower_id}", 0)
    return f"cleared shower{shower_id}"

def error_handler(error):
    exception_type = error.__class__.__name__
    exception_message = str(error)
    result_error = { 
        "error": { 
        "type": exception_type, 
        "message": exception_message 
        }
    }
    return jsonify(result_error)



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
# check_shower
# TODO: warn if stopped (logfile?)
def incr():
    showers = running_showers()
    for k,v in enumerate(showers):
        if int(v or 0) == 1:
            shower = 'shower_time_sum:' + str(k+1)
            accumulated_shower_time = redis.incr(shower)
            print(shower)
            print(accumulated_shower_time)
#    return
  


@celery.task
def escort_user(user, shower, seconds):
    text = f"Hello, {user}. Welcome to the Wrongtown Shower System! Please use shower {shower}. You have {seconds} seconds of shower time. Enjoy! Shower {shower}, shower {shower}, shower {shower}"
    print(text)
    if platform.system() == 'Darwin':
        os.system("say " + text)
    else:
        os.system(f"espeak-ng '{text}' --stdout | aplay")

# Helper functions

def running_showers():
    return redis.mget('shower1', 'shower2')

def shower_pin(id):
    return SHOWER_PIN_MAP[id]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


