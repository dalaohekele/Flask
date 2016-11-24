from flask import Flask,render_template
from flask import request
from flask import make_response
from flask_script import Manager
from flask.ext.bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required

app = Flask(__name__)

app.config['SECRET_KEY']='hard to guess string'

bootstrap = Bootstrap(app)
moment=Moment(app)



class NameForm(Form):
    name=StringField('What is your name',validators=[Required()])
    submit=SubmitField('Submit')




@app.route('/',methods=['GET','POST'])
def index():
    name=None
    form = NameForm()
    if form.validate_on_submit():
        name=form.name.data
        form.name.data=''
    return render_template('index.html', form=form, name=name)


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
