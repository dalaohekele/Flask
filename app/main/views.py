# coding=utf-8

from flask import render_template,abort,flash,url_for,redirect,request,current_app,make_response
from flask_login import login_required,current_user
from .forms import EditProfileForm,EditProfileAdminForm,PostForm
from .. import db
from . import main
from ..models import User,Role,Post,Permission
from ..decorators import admin_required,permission_required

import sys
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
    return render_template('index.html',form=form,posts=posts,show_followed=show_followed,pagination=pagination)

# 用户不存在的路由
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,per_page=10,error_out=False)
    posts = pagination.items
    return render_template('user.html',user=user,posts=posts,pagination=pagination)


# 资料界面路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('资料已更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

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
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

# 博客详情页
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])

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
        flash('博客已更新')
        return redirect(url_for('.post',id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html',form=form)

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
    return render_template('followers.html',user=user,title="关注我的",
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
    return render_template('followers.html',user=user,title="我关注的",
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
