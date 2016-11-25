# coding=utf-8
import os
from flask import Flask,render_template,session,redirect,url_for,flash
from flask import make_response
from flask.ext.bootstrap import Bootstrap
from flask_moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy

import sys
reload(sys)
sys.setdefaultencoding('utf8')


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=\
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['SECRET_KEY']='hard to guess string'

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment=Moment(app)



class NameForm(Form):
    name=StringField('What is your name',validators=[Required()])
    submit=SubmitField('Submit')

class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return'<User %r>' % self.username




@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('用户名变更')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

@app.route('/cookies')
def cookies():
    response=make_response('<h1>this document carries a cookies</h1>')
    response.set_cookid('answer','42')
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')

if __name__ == '__main__':
    app.run()
