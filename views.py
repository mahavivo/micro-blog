#!/usr/bin/env python
# -*- coding: utf-8 -*-


from common import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, LoginManager, login_required
from forms import LoginForm, PostForm
from models import User, Post

from datetime import datetime
from sqlalchemy import desc


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    posts = Post.query.order_by(desc('id')).all()
    return render_template("posts.html", posts=posts)


@app.route('/post/<int:id>', methods=['GET'])
def post(id):
    post = Post.query.filter_by(id=id).first()
    if post == None:
        flash('Post not found.')
        return redirect(url_for('index'))
    return render_template("post_detail.html", post=post)


@app.route('/admin/create-admin', methods=['GET'])
def create_admin():
    user = User(username='vivo', email='test@126.com')
    user.set_password('123456')
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.verify_password(form.password.data):
                login_user(user)
                flash('Logged in successfully')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong credentials')
                return redirect(url_for('login'))
    return render_template('admin/login.html', form=form)


@app.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    posts = Post.query.order_by(desc('id')).all()
    return render_template("admin/dashboard.html", posts=posts)


@app.route('/admin/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            pub_date = datetime.now()
            post = Post(title=title, content=content, pub_date=pub_date)
            db.session.add(post)
            db.session.commit()
            flash('Post added!')
            return redirect(url_for('add_post'))
    return render_template('admin/add_post.html', form=form)


@app.route('/admin/post/update/<id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = PostForm()
    post = Post.query.get_or_404(id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated!')
        return redirect(url_for('update', id=post.id))

    form.title.data = post.title
    form.content.data = post.content
    return render_template('admin/update_post.html', form=form)


@app.route('/admin/post/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()

    p1 = Post(title='雨霖鈴',
              content='寒蟬淒切，對長亭晚，驟雨初歇。都門帳飲無緒，留戀處，蘭舟催發。'
                      '執手相看淚眼，竟無語凝噎。念去去，千裏煙波，暮霭沈沈楚天闊。'
                      '多情自古傷離別，更那堪，冷落清秋節！今宵酒醒何處？楊柳岸，曉風殘月。'
                      '此去經年，應是良辰好景虛設。便縱有千種風情，更與何人說？',
              pub_date=datetime.now())
    p2 = Post(title='Walden',
              content='Time is but the stream I go a-fishing in. I drink at it; '
                      'but while I drink I see the sandy bottom '
                      'and detect how shallow it is. Its thin current slides away, '
                      'but eternity remains. I would drink deeper; '
                      'fish in the sky, whose bottom is pebbly with stars.',
              pub_date=datetime.now())

    db.session.add(p1)
    db.session.add(p2)
    db.session.commit()

    app.run(debug=True)