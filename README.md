

# System Requirements

`apt install espeak redis-server sqlite3 virtualenv espeak-ng`

```
virtualenv -p python3.7 .venv
. .venv/bin/activate
pip install -r requirements.txt
python create_db.py
```

# Seed data
.mode csv
.import w.csv users
```
INSERT INTO users VALUES(1,' kitchen_admin','kitchen Admin','99887',99, 1);
INSERT INTO users VALUES(2,'aaa','A A A','92629',99, 0);
INSERT INTO users VALUES(112,'Marshal Lane','Marshal Lane','485666',12, 0);
INSERT INTO showers VALUES(1,NULL,NULL,NULL,NULL);
INSERT INTO showers VALUES(2,NULL,NULL,NULL,NULL);
INSERT INTO phrases VALUES(1, 'You look hot');
INSERT INTO phrases VALUES(2, 'Enjoying it?');
INSERT INTO phrases VALUES(3, 'You are doing well');

INSERT INTO users VALUES(113,'Jun Soto','Jun Soto','381007',12, 0);
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
