# coding=utf-8
from flask.ext.wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

# 添加中文支持
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class LoginForm(Form):
    email = StringField('邮箱',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('密码',validators=[DataRequired()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    email = StringField('邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('用户名',validators=[DataRequired(),Length(1,64),
                                                  Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                                         '用户名必须由字母、数字、下划线、点号组成')])
    password = PasswordField('密码',validators=[DataRequired(),EqualTo('password2',message='密码不一致')])
    password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码',validators=[DataRequired()])
    password = PasswordField('新密码',validators=[DataRequired(),EqualTo('password2',message='密码不一致')])
    password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('提交')

class PasswordResetRequestForm(Form):
    email = StringField('邮箱',validators=[DataRequired(),Length(1,64),Email()])
    submit = SubmitField('重置密码')

class PasswordResetForm(Form):
    email = StringField('邮箱',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('新密码',validators=[DataRequired(),EqualTo('password2',message='密码不一致')])
    password2 = PasswordField('确认密码',validaotrs=[DataRequired()])
    submit = SubmitField('重置密码')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('无效邮箱地址')

class ChangeEmailForm(Form):
    email = StringField('新邮箱',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('密码',validators=[DataRequired()])
    submit = SubmitField('邮箱地址已更改')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱地址已存在')
