# coding=utf-8

import sys,os
import random
import urllib
import datetime
from flask import render_template,abort,flash,url_for,redirect,request,current_app,make_response
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
from app.table.models import User,Role,Post,Permission,Comment
from . import main
from .forms import EditProfileForm,EditProfileAdminForm,PostForm,CommentForm
from .. import db
from ..decorators import admin_required,permission_required
from uploader import Uploader
reload(sys)
sys.setdefaultencoding('utf-8')


# views中编写对应程序的路由

# 主界面路由
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # 显示所有博客文章或只显示所关注用户的文章
    page = request.args.get('page',1,type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(page,per_page=10,error_out=False)
    posts = pagination.items
    return render_template('main/index.html',form=form,posts=posts,show_followed=show_followed,pagination=pagination)

# 用户不存在的路由
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,per_page=10,error_out=False)
    posts = pagination.items
    return render_template('user/user.html',user=user,posts=posts,pagination=pagination)


# 资料界面路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        # 新增提交用户头像
        avatar = request.files['avatar']
        fname = avatar.filename
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
        flag = '.' in fname and fname.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
        if not flag:
            flash('文件类型错误')
            return redirect(url_for('.user', username=current_user.username))
        avatar.save('{}{}_{}'.format(UPLOAD_FOLDER, current_user.username, fname))
        current_user.real_avatar = '/static/avatar/{}_{}'.format(current_user.username, fname)
        db.session.add(current_user)
        flash('资料已更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('user/edit_profile.html', form=form)

# 管理员资料页面路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('资料已更新')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('user/edit_profile.html', form=form, user=user)

# 博客详情页
# 评论路由
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('评论已提交')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('blog/post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)

# 编辑博客文章的路由
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user !=post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('博客已更新')
        return redirect(url_for('.post',id=post.id))
    form.body.data = post.body
    return render_template('blog/edit_post.html',form=form)

# 关注的路由
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('请先登录')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('您已经关注了该用户')
        return redirect(url_for('.user',username=username))
    current_user.follow(user)
    flash('成功关注 %s'%username)
    return redirect(url_for('.user',username=username))

# 取消关注的路由
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('请先登录')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你还没有关注这个用户')
        return redirect(url_for('.user',username=username))
    current_user.unfollow(user)
    flash('不再关注用户 %s ' % username)
    return redirect(url_for('.user',username=username))


# 关注者的路由
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('请先登录')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(page,per_page=10,error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp}
               for item in pagination.items]
    return render_template('user/followers.html',user=user,title="关注我的",
                           endpoint='.followers',pagination=pagination,
                           follows=follows)

@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('请先登录')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(page,per_page=10,error_out=False)
    follows = [{'user':item.followed,'timestamp':item.timestamp}
               for item in pagination.items]
    return render_template('user/followers.html',user=user,title="我关注的",
                           endpoint='.followed_by',pagination=pagination,
                           follows=follows)


# 查询所有文章
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

# 查询关注者的文章
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

# 管理评论的路由
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('blog/moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

