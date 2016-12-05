# coding=utf-8
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired

# 添加中文支持
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class NameForm(Form):
    name = StringField('你的名字',validators=[DataRequired()])
    submit = SubmitField('Submit')