# coding=utf-8
from flask_wtf import Form
from wtforms import StringField,TextAreaField,SubmitField,BooleanField,SelectField
from wtforms.validators import DataRequired,Length,Email,Regexp
from wtforms import ValidationError
from ..models import Role, User

# 添加中文支持
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class NameForm(Form):
    name = StringField('你的名字',validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileForm(Form):
    name = StringField('真实姓名',validators=[Length(0,64)])
    location = StringField('地址',validators=[Length(0,64)])
    about_me = TextAreaField('自我描述')
    submit = SubmitField('提交')


class EditProfileAdminForm(Form):
    email = StringField('邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('用户名',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z0-9_.]*$',0,
                                                                                '用户名必须由字母、数字、下划线、点号组成')])
    confirmed = BooleanField('是否认证')
    roel = SelectField('角色',coerce=int)
    name = StringField('真实姓名',validators=[Length(0,64)])
    location = StringField('地址',validators=[Length(0,64)])
    about_me = TextAreaField('自我描述')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate(self,field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')


    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

