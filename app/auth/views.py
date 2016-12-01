# coding=utf-8
from flask import render_template,redirect,request,url_for,flash
from flask.ext.login import login_user,logout_user,login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,RegistrationForm

# 添加中文支持
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash('你现在可以登录了!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)


@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的用户名或密码')
    return render_template('auth/login.html',form=form)

@auth.route('logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出系统')
    return redirect(url_for('main.index'))

