

# System Requirements

`apt install espeak redis-server sqlite3 virtualenv`

```
virtualenv -p python3 .venv
. .venv/bin/activate
pip install -r requirements.txt
python create_db.py
```

# Seed data

```
INSERT INTO users VALUES(1,'test','test@test.com','test',70);
INSERT INTO users VALUES(2,'aaa',NULL,NULL,18);
INSERT INTO showers VALUES(1,1,NULL,NULL,90);
INSERT INTO showers VALUES(2,NULL,NULL,NULL,NULL);
```

# Run

main site

`python app.py`

workers

```
celery -A app.celery worker -l info -E
celery -A app.celery beat -l info
```

# Mac Development

install emulator

`pip install git+https://github.com/nosix/raspberry-gpio-emulator/`

