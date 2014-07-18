#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import base64
from urlparse import urljoin
import hashlib

import feedparser
from flask import Flask, flash, redirect, request, render_template, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from readability import ParserClient
from werkzeug.contrib.atom import AtomFeed
from apscheduler.scheduler import Scheduler

import config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = config.SQLALCHEMY_ECHO
app.secret_key = config.APP_SECRET_KEY

readability_apy_key = config.READABILITY_API_KEY

db = SQLAlchemy(app)
rss_sched = Scheduler()


class ReverseProxied(object):
    """
    Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
            proxy_pass http://192.168.0.1:8002;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Scheme $scheme;
            proxy_set_header X-Script-Name /myprefix;
    }

    :param app: the WSGI application
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


class MainTable(db.Model):
    __tablename__ = 'html'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    time_stamp = db.Column(db.DateTime, unique=False, nullable=False)
    url = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=True, unique=False)
    body = db.Column(db.Text, nullable=True, unique=False)
    archived = db.Column(db.Boolean, unique=False, nullable=False, default=False)


class Feeds(db.Model):
    __tablename__ = 'rss'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    url = db.Column(db.String, nullable=False, unique=True)


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    time_stamp = db.Column(db.DateTime, unique=False, nullable=False)
    src_key = db.Column(db.String, nullable=True, unique=False)
    url = db.Column(db.String, nullable=True, unique=False)
    title = db.Column(db.String, nullable=True, unique=False)


@app.before_first_request
def run():
    db.create_all()


@app.route('/')
def page_list():
    # todo pagination
    values = MainTable.query.filter_by(archived=False).with_entities(MainTable.id, MainTable.time_stamp, MainTable.url, MainTable.title).order_by(MainTable.time_stamp.desc()).all()
    return render_template('topic_list.html', title=u"Astatum - Список статей", tab_values=values,
                           secret=hashlib.md5(config.APP_SECRET_KEY).hexdigest())


@app.route('/archive')
def archive_page_list():
    # todo pagination
    values = MainTable.query.filter_by(archived=True).with_entities(MainTable.id, MainTable.time_stamp, MainTable.url, MainTable.title).order_by(MainTable.time_stamp.desc()).all()
    return render_template('archive_list.html', title=u"Astatum - Архив", tab_values=values,
                           secret=hashlib.md5(config.APP_SECRET_KEY).hexdigest())


@app.route('/save', methods=['GET', 'POST'])
def save_page():
    # if request.method == 'POST':
    #     url = request.form['url']
    #
    #     parser_client = ParserClient(readability_apy_key)
    #     parser_response = parser_client.get_article_content(url)
    #
    #     save_to_db(url, parser_response.content['title'], parser_response.content['content'])
    #
    #     flash(u'Добавлено: ' + parser_response.content['title'], 'success')
    #     return redirect(url_for('page_list'))

    if request.method == 'GET' and request.args.get('action') and request.args.get('key') == hashlib.md5(
            config.APP_SECRET_KEY).hexdigest():
        url = base64.decodestring(request.args.get('url'))

        if request.url_root == url:
            return redirect(url_for('page_list'))

        parser_client = ParserClient(readability_apy_key)
        parser_response = parser_client.get_article_content(url)
        flash(u'Добавлено: ' + parser_response.content['title'], 'success')

        write_log('add', url=url, title=parser_response.content['title'])
        save_to_db(url, parser_response.content['title'], parser_response.content['content'])

        return redirect(url_for('page_list'))

    else:
        return redirect(url_for('page_list'))


@app.route('/view', methods=['GET', 'POST'])
@app.route('/view/<page_id>', methods=['GET', 'POST'])
def view_page(page_id=1):
    content = MainTable.query.get_or_404(page_id)
    return render_template('view.html', post=content, ref=request.referrer)


@app.route('/del/<int:page_id>',  methods=['GET', 'POST'])
def del_page(page_id):
    row = MainTable.query.get_or_404(page_id)
    flash(u'Удалено: ' + row.title, 'danger')
    write_log('del', url=row.url, title=row.title)
    db.session.delete(row)
    db.session.commit()
    return redirect(redirect_url())


@app.route('/archive/<int:page_id>')
def save_page_to_archive(page_id):
    row = MainTable.query.get_or_404(page_id)
    row.archived = True
    flash(u'Помещено в архив: ' + row.title, 'warning')
    write_log('arch', url=row.url, title=row.title)
    db.session.commit()
    return redirect(url_for('page_list'))


@app.route('/log')
def log_page():
    values = Log.query.order_by(Log.time_stamp.desc()).limit(100).all()
    return render_template('log_list.html', title=u"Astatum - Log", tab_values=values)


@app.route('/feed.atom')
def recent_feed():
    feed = AtomFeed('Astatum posts', feed_url=request.url, url=request.url_root)
    articles = MainTable.query.order_by(MainTable.time_stamp.desc()).limit(15).all()
    for article in articles:
        feed.add(article.title, unicode(article.body),
                 content_type='html',
                 url=urljoin(request.url_root, url_for('view_page') + '/' + str(article.id)),
                 updated=article.time_stamp,
                 published=article.time_stamp)

    return feed.get_response()


@rss_sched.interval_schedule(minutes=config.INTERVAL)
def get_feed():
    parsed_feed = feedparser.parse(config.RSS_FEED)
    parser_client = ParserClient(readability_apy_key)

    feed_urls_cached = Feeds.query.all()

    db_url_list = [cached_feed.url for cached_feed in feed_urls_cached]

    for rss_url in parsed_feed['entries']:
        if rss_url['link'] not in db_url_list:
            parser_response = parser_client.get_article_content(rss_url['link'])
            add_feed = Feeds(url=rss_url['link'])
            write_log('rss', url=rss_url['link'], title=parser_response.content['title'])
            db.session.add(add_feed)
            if save_to_db(rss_url['link'], parser_response.content['title'], parser_response.content['content']):
            db.session.commit()


def redirect_url(default='page_list'):
    return request.args.get('next') or \
        request.referrer or \
        url_for(default)


def save_to_db(page_url, page_title, page_body):
    try:
        row = MainTable(time_stamp=datetime.datetime.now(), url=page_url, body=page_body, title=page_title)
        db.session.add(row)
        db.session.commit()
        return True
    except:
        return False


def write_log(src_key, url, title):
    if src_key == 'rss':
        src_key = 'cloud-download'
    elif src_key == 'del':
        src_key = 'minus-sign'
    elif src_key == 'add':
        src_key = 'plus-sign'
    elif src_key == 'arch':
        src_key = 'bookmark'
    else:
        src_key = 'question-sign'

    try:
        row = Log(time_stamp=datetime.datetime.now(), url=url, src_key=src_key, title=title)
        db.session.add(row)
        db.session.commit()
        return True
    except:
        return False


if __name__ == '__main__':

    if config.RSS_CHECK_ENABLED:
        rss_sched.start()
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.run(host=config.BIND_ADDR, debug=config.DEBUG, port=config.BIND_PORT)
