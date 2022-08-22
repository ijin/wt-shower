# coding: utf-8
from flask import Flask, Response, render_template, request, redirect, url_for, flash, session, jsonify
from flask_api import status 
from database import db_session
from models import User, Shower, Phrase, Event
from celery import Celery
from celery.schedules import crontab
from datetime import datetime

import os
import random
import platform
import redis
import json
import nfc
import queue
#import RPi.GPIO as GPIO
#import piplates.RELAYplate as RELAY

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(11, GPIO.OUT)
#GPIO.setup(12, GPIO.OUT)


SHOWER_PIN_MAP = { 1:11, 2:12}
PAUSE_TIME_UNTIL_RESET = 30
PAUSE_TIME_WARNING = PAUSE_TIME_UNTIL_RESET - 15
SINK_TIME = 600 # seconds
SINK_STOP_BUFFER = 5 # seconds
SINK_ID = 3

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

phrase_count = Phrase.query.count()




####  SSE

class MessageAnnouncer:

    def __init__(self):
        self.listeners = []

    def listen(self):
        self.listeners.append(queue.Queue(maxsize=5))
        return self.listeners[-1]

    def announce(self, msg):
        # We go in reverse order because we might have to delete an element, which will shift the
        # indices backward
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]

announcer = MessageAnnouncer()

def format_sse(data: str, event=None) -> str:
    """Formats a string and an event name in order to follow the event stream convention.
    >>> format_sse(data=json.dumps({'abc': 123}), event='Jackson 5')
    'event: Jackson 5\\ndata: {"abc": 123}\\n\\n'
    """
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

@app.route('/ping')
def ping():
    msg = format_sse(data='{"nfc":false}')
    announcer.announce(msg=msg)
    return {}, 200

@app.route('/ping2')
def ping2():
    msg = format_sse(data='{"nfc":true}')
    announcer.announce(msg=msg)
    return {}, 200


@app.route('/listen', methods=['GET'])
def listen():

    def stream():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    return Response(stream(), mimetype='text/event-stream')

####



def log_event(uid, credits, kitchen=0, timestamp=datetime.now()):
    os.system(f"echo '{timestamp}, {uid}, {credits}, {kitchen}'>> log.csv")

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def index():
    u = User.query.with_entities(User.name).order_by(User.name).all()
    return render_template('login.html', users=u)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        print(f"{name}, {password}")
        u = User.query.filter(User.name == name, User.password == password).first()
        if u:
            session['id'] = u.id
            flash('You were successfully logged in')
            if u.chef:
                return render_template('kitchen.html', name=u.name)
            else:
                return redirect(url_for('selection'))
        else:
            flash('Wrong credentials!')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/login_nfc', methods = ['POST', 'GET'])
def login_nfc():
    if request.method == 'POST':
        nfc = request.form['nfc']
        print(f"{nfc}")
        u = User.query.filter(User.nfc == nfc).first()
        if u:
            session['id'] = u.id
            flash('You were successfully logged in')
            if u.chef:
                return render_template('kitchen.html', name=u.name)
            else:
                return redirect(url_for('selection'))
        else:
            flash('Wrong credentials!')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/kitchen', methods = ['GET'])
def kitchen():
    u = User.query.get(session['id'])
    if u.chef:
        #return render_template(url_for('kitchen'))
        return render_template('kitchen.html')
    else:
        #return render_template(url_for('selection'))
        return render_template('selection.html')

@app.route('/sink', methods = ['POST'])
def sink():
    u = User.query.get(session['id'])
    if u.chef:
        print('running sink')
        #RELAY.relayON(3,int(SINK_ID))
        log_event(u.id, 0, 1)
        enable_sink()
    return render_template('sink.html')

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
    if user.credits <= 0:
        return render_template('no_credits.html')
    else:
        log_event(user.id, credits)
        assign_shower(shower, user, credits)
        seconds = int(credits)*90
        escort_user(user.pi_name, shower.id, seconds)
        return render_template('instructions.html', seconds=seconds, credits=user.credits, shower=shower.id)

# TODO: OOP
def available_shower():
    showers = Shower.query.filter_by(assigned_to=None).all()
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
    shower.assigned_to = user.pi_name
    shower.seconds_allocated = seconds
    db_session.commit()
    redis.set(f"shower{shower.id}", 0)
    redis.set(f"shower_time_sum:{shower.id}", 0)
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
    escort_user(name, 50, 100)
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
        #GPIO.output(shower_pin(shower_id), not toggle_status) # 1 == off
        RELAY.relayTOGGLE(3,int(shower_id))
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

@app.route('/api/shower_toggle/<shower_id>')
def shower_toggle(shower_id):
    #shower = Shower.query.filter_by(id=shower_id, not(assigned_to=None)).first()
    shower = Shower.query.get(shower_id)
    if shower.assigned_to == None:
        r  = f"shower{shower_id} NOT ASSIGNED"
        return r
    else:
        # TODO: DRY
        shower_status = int(redis.get(f"shower{shower_id}") or 0)
        toggle_status = not bool(shower_status)
        #GPIO.output(shower_pin(int(shower_id)), not toggle_status) # 1 == off
        #RELAY.relayTOGGLE(3,int(shower_id))
        redis.set(f"shower{shower_id}", int(toggle_status))
        if int(toggle_status) == 1 and shower.started_at == None: # first shower
            shower.started_at = datetime.now()
            db_session.commit()
        elif int(toggle_status) == 0: # pause
            shower.paused_at = datetime.now()
            db_session.commit()
        return f"shower{shower_id}, status:{toggle_status}"


# test
@app.route('/api/shower_off/<shower_id>', methods = ['GET'])
def shower_off(shower_id):
    try:
        #j = request.get_json()
        #shower_id = j['shower']
        #GPIO.output(shower_pin(int(shower_id)), 1)
        RELAY.relayOFF(3,int(shower_id))
        redis.set(f"shower{shower_id}", 0)
        return "off"
    except Exception as e:
        result = error_handler(e)
        return result, status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/api/shower_clear/<shower_id>', methods = ['GET'])
def shower_clear(shower_id):
    shower_shutdown(shower_id)
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
        # if showers are running
        if int(v or 0) == 1:
            shower_id = k+1
            shower = f"shower_time_sum:{shower_id}"
            accumulated_shower_time = redis.incr(shower)
            print(f"Shower {shower_id}: total time used: {accumulated_shower_time}")
            s = Shower.query.filter_by(id=shower_id).first()
            time_left = s.seconds_allocated - accumulated_shower_time 
            print(f"time_left: {time_left}")

            if accumulated_shower_time == 20:
                index = random.randint(0, phrase_count-1)
                phrase = Phrase.query.get(index).phrase
                text = f"Hey, {s.assigned_to}, {phrase}"
                say.delay(text)
                print("20 seconds in")
            if time_left == 30:
                text = f"Hey, {s.assigned_to}, 30 seconds left.."
                print(text)
                say.delay(text)
            elif time_left <= 0:
                text = "TIMES UP......"
                print(text)
                shower_shutdown(shower_id)
                say(text)
                break
        # if showers are stopped
        elif (not v == None):
            shower_id = k+1
            s = Shower.query.filter_by(id=shower_id).first()
            if (not s.paused_at == None) and (not s.assigned_to == None):
                elapsed_pause = (datetime.now() - s.paused_at).total_seconds()
                print (f"Shower {shower_id}")
                print (f"Elapsed time since last pause: {elapsed_pause}")
                if elapsed_pause > PAUSE_TIME_UNTIL_RESET:
                    text = f"Hey {s.assigned_to}, Shower {shower_id} paused for too long..."
                    say(text)
                    shower_shutdown(shower_id)
                    break
                if elapsed_pause > PAUSE_TIME_WARNING:
                    text = f"Shower {shower_id} paused for a while. Shutting down unless it's resumed"
                    say.delay(text)
    #if running_sink():
    sink_ttl = running_sink_ttl()
    if (sink_ttl > 0 and sink_ttl <= SINK_STOP_BUFFER):
        print(f"stopping sink..")
        #RELAY.relayOFF(3,int(SINK_ID))
    elif (sink_ttl > SINK_STOP_BUFFER):
        print(f"sink is running. stopping in {redis.ttl('sink')}")
    else:
        print("sink stopped")

def shower_shutdown(shower_id):
    db_session.query(Shower).filter_by(id=shower_id).update(dict(assigned_to=None,started_at=None,paused_at=None,seconds_allocated=None))
    db_session.commit()
    #GPIO.output(shower_pin(int(shower_id)), 1)
    #RELAY.relayOFF(3,int(shower_id))
    redis.delete(f"shower{shower_id}")
    redis.set(f"shower_time_sum:{shower_id}", 0)
    text = f"Shutting down shower {shower_id}"
    print(text)
    say.delay(text)


def escort_user(user, shower, seconds):
    text = f"Hello, {user}. Welcome to the Wrongtown Shower System! Please use shower {shower}. You have {seconds} seconds of shower time. Enjoy! Shower {shower}, shower {shower}, shower {shower}"
    print(text)
    say.delay(text)

# Helper functions
@celery.task
def say(text):
    if platform.system() == 'Darwin':
        os.system("say " + text)
    else:
        os.system(f"espeak-ng '{text}' --stdout | aplay")

def running_showers():
    return redis.mget('shower1', 'shower2')

def enable_sink():
    return redis.set('sink', 1, SINK_TIME + SINK_STOP_BUFFER)

def running_sink_ttl():
    #return redis.get('sink')
    return redis.ttl('sink')

def shower_pin(id):
    return SHOWER_PIN_MAP[id]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

