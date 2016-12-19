# coding=utf-8
import sys

from flask import render_template,redirect,request,url_for,flash
from flask.ext.login import current_user
from flask.ext.login import login_user,logout_user,login_required

from app.table.models import User
from . import auth
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,PasswordResetForm,\
    PasswordResetRequestForm,ChangeEmailForm
from .. import db
from ..email import send_email

reload(sys)
sys.setdefaultencoding('utf-8')


@auth.before_app_request
def before_request():
    if current_user.is_authenticated :
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.'\
        and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的用户名或密码')
    return render_template('auth/login.html', form=form)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出系统')
    return redirect(url_for('main.index'))



@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '请确认验证码', 'auth/email/confirm', user=user, token=token)
        flash('验证码已发送至您的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)



@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirmed(token):
        flash('通过验证')
    else:
        flash('验证码错误')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'确认您的账户','auth/email/confirm',user=current_user,token=token)
    flash('新的验证邮件已将发往您的邮箱')
    return redirect(url_for('main.index'))



@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('密码修改成功')
            return redirect(url_for('main.index'))
        else:
            flash('密码错误')


    return render_template("auth/change_password.html",form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重置密码',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('邮件已发送至您的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('你的密码已经被重置')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email',methods=['GET','POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '确认你的邮箱地址',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('邮件已发送至您的邮箱')
            return redirect(url_for('main.index'))
        else:
            flash('无效的邮箱或密码')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('你的邮箱地址已更新')
    else:
        flash('无效的请求')
    return redirect(url_for('main.index'))

