#!/usr/bin/env python2
# -*- coding: utf-8 -*-


BIND_ADDR = '0.0.0.0'
BIND_PORT = 8002

# session enc key, any random string
APP_SECRET_KEY = ""

# https://www.readability.com/developers/api/reader
READABILITY_API_KEY = ''

# DATABASE_URI = 'postgresql://scott:secret@localhost/mydatabase'
# DATABASE_URI = 'mysql://scott:secret@localhost/mydatabase'
# DATABASE_URI = 'sqlite:////absolute/path/to/foo.db'

# appfog config
# import os
# import json
# services = json.loads(os.getenv("VCAP_SERVICES", "{}"))
# mysql_env = services["mysql-5.1"][0]["credentials"]
# DATABASE_URI = "mysql://%s:%s@%s:%d/%s" %\
#                (mysql_env['username'],
#                 mysql_env['password'],
#                 mysql_env['host'],
#                 mysql_env['port'],
#                 mysql_env['name'])

DATABASE_URI = 'sqlite:///data.db'

# debug ORM requests
SQLALCHEMY_ECHO = False

# enable app debug
DEBUG = False

# Posts from feed will be added automatically
RSS_CHECK_ENABLED = False
RSS_FEED = 'http://tiny.gov/rss/public.php?op=rss&id=-1&key=XXXXXXXX'
INTERVAL = 5  # in minutes
