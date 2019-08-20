

# System Requirements

`apt install espeak redis-server sqlite3 virtualenv espeak-ng`

```
virtualenv -p python3.7 .venv
. .venv/bin/activate
pip install -r requirements.txt
python create_db.py
```

# Seed data

```
INSERT INTO users VALUES(1,'test','1234',99, 0);
INSERT INTO users VALUES(2,'chef','1111',99, 1);
INSERT INTO users VALUES(3,'aaa','222',99, 0);
INSERT INTO showers VALUES(1,0,NULL,NULL,90);
INSERT INTO showers VALUES(2,1,NULL,NULL,NULL);
```

# Run

main site

`python app.py`

workers

```
celery -A app.celery worker -l info -E
celery -A app.celery beat -l info
```

swtich control

```
python hello_gpio2.py
```

# Mac Development

install emulator

`pip install git+https://github.com/nosix/raspberry-gpio-emulator/`


# Debug

```
watch -n1 gpio readall
watch -n1 "sqlite3 -header app.db 'select * from showers' "
```
