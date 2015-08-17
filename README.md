Astatum
=======

Simple self hosted Pocket/Readability service with storage articles entirely.

![](http://cl.ly/image/2J3A3q3x3f0P/Image%202014-07-18%20at%2010.03.44%20%D0%B4%D0%BE%20%D0%BF%D0%BE%D0%BB%D1%83%D0%B4%D0%BD%D1%8F.png "Main")

![](http://cl.ly/image/2j1B1u2A3G45/Image%202014-07-18%20at%2010.04.18%20%D0%B4%D0%BE%20%D0%BF%D0%BE%D0%BB%D1%83%D0%B4%D0%BD%D1%8F.png "Log")

## Installation
Run this commands in Linux bash:
```sh
$ mkdir /srv
$ cd /srv
$ git clone https://github.com/x0x01/astatum.git
$ cd astatum
$ chmod 777 static/img
$ pip install -r requirements.txt
Отредактировать (при необходимости) config.py
$ python astatum.py
```
If installation was completed without error http://your_server_ip:8082/ in browser (you can change port number in file config.py).

## Features
- Transmission full articles text to RSS
- Button "To bookmarks!", that can save any articles in browser
- Load articles from RSS
- Local cache for images
- Using `readability` for parsing HTML
- Python, Flask, SQLAlchemy, Bootstrap 3


