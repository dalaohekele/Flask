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

    # 初始化函数  def__int__()
    # 在建立models的时候，Role类里面有一个relationship，他的backref是"role"，
    # 我自己理解，这个就是对应User 类创建实例时，User能够通过role属性，来访问Role类，并将Role类的类对象，作为本身User的一个属性来起作用
    # 说白了点，就是，将Role类的所有属性打包进一个实例，赋值给User的role属性。
    # 所以，在书本上的例子里，你选择了不同的role，就等于选择了不同的用户权限等级。
    def __init__(self, user, *args, **kwargs):
        # super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        # 首先找到EditProfileAdminForm 的父类 Form,然后把EditProfileAdminForm的对象self转化为父类Form的对象
        # 然后被转换的类Form对象自己调用自己的__init__()函数
        # 普通继承和super继承是一样的。但是其实它们的内部运行机制不一样，这一点在多重继承时体现得很明显。在super机制里可以保证公共父类仅被执行一次，
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user


    # 如果设定的函数是以validate_开头的，那么，他会在验证的时候，和上面表单的普通验证一起使用。
    # validate_email ,下划线后面的内容，对应上面表单的名字，再具体一些，对应的是form.email，也就是Form实例对象的email属性。
    # 所以field.data这句意思实际上是form.email.data != self.user.username 。
    def validate(self,field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')


    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

