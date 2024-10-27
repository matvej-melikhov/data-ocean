from urllib.parse import urlparse

from flask import render_template, request, redirect, url_for, flash, abort, make_response, g, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _

import re
import sqlite3
import markdown


def render_markdown(text):
    """Markdown → HTML с защитой LaTeX-блоков от парсера."""
    blocks = []

    def protect(m):
        blocks.append(m.group(0))
        return f'\x00MATH{len(blocks) - 1}\x00'

    # Сначала защищаем блочные $$ ... $$
    text = re.sub(r'\$\$[\s\S]+?\$\$', protect, text)
    # Затем инлайн $ ... $ (не $$)
    text = re.sub(r'(?<!\$)\$(?!\$).+?(?<!\$)\$(?!\$)', protect, text)

    html = markdown.markdown(text, extensions=['fenced_code', 'codehilite', 'tables'])

    # Восстанавливаем LaTeX
    for i, block in enumerate(blocks):
        html = html.replace(f'\x00MATH{i}\x00', block)

    return html

from app import application
from app.forms import *
from app.models import *


# для загрузки темы в каждом маршруте
@application.before_request
def load_theme():
    g.theme = request.cookies.get('theme') or 'light'  # По умолчанию светлая тема


@application.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('login'))


@application.route("/")
def index():
    post_count = Post.query.count()
    user_count = User.query.count()
    tag_count  = Tag.query.count()
    latest     = Post.query.order_by(-Post.id).first()
    return render_template("index.html",
                           post_count=post_count,
                           user_count=user_count,
                           tag_count=tag_count,
                           latest=latest)

@application.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegForm()

    if current_user.is_authenticated:
        return redirect(url_for("blog"))

    if request.method == "POST":
        name = request.form.get("name")
        last_name = request.form.get("last_name")
        login = request.form.get("login")
        password = request.form.get("password")
        avatar_file = request.files.get("avatar")
        avatar = sqlite3.Binary(avatar_file.read()) if avatar_file and avatar_file.filename else None

        user = User(name=name, last_name=last_name, login=login, avatar=avatar)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("blog"))

    return render_template("registration.html", form=form)

@application.route("/login", methods=["GET", "POST"])
def login():
    next = request.args.get("next")

    if current_user.is_authenticated:
        return redirect(url_for("blog"))

    if request.method == "POST":
        user_login = request.form.get("login")
        user_password = request.form.get("password")
        user = User.query.filter_by(login=user_login).first()
        if user and user.check_password(user_password):
            login_user(user)
            flash(_('Вы успешно авторизовались!'))
            safe_next = next if next and urlparse(next).netloc == '' else None
            return redirect(safe_next) if safe_next else redirect(url_for("blog"))
        else:
            flash(_('Неверный логин или пароль!'))
            return redirect(url_for("login"))

    form = LoginForm()
    return render_template("login.html", form=form)

@application.route("/logout")
def logout():
    logout_user()
    flash(_('Вы вышли из аккаунта'))
    return redirect(url_for("index"))

@application.route("/blog")
@login_required
def blog():
    page = request.args.get("page")
    page = int(page) if page and page.isdigit() else 1

    posts = Post.query.order_by(-Post.id)
    pages = posts.paginate(page=page, per_page=5)

    return render_template("blog.html", pages=pages)

@application.route("/search")
@login_required
def search():
    s = request.args.get('s', '')

    page = request.args.get("page")
    page = int(page) if page and page.isdigit() else 1

    posts = Post.query.filter(Post.title.contains(s) | Post.content.contains(s) | Post.description.contains(s)).order_by(-Post.id)
    pages = posts.paginate(page=page, per_page=5)

    return render_template("search.html", pages=pages)

@application.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    form = CreatePostForm()
    all_tags = Tag.query.all()

    if request.method == "POST":
        if form.validate():
            title = request.form.get("title")
            description = request.form.get("description")
            content = request.form.get("content")
            tags = [Tag.query.filter_by(name=name).first() for name in request.form.getlist("tag")]
            new_post = Post(title=title, content=content, description=description)
            new_post.tags = tags
            db.session.add(new_post)
            db.session.commit()
            flash(_('Пост создан!'))
            return redirect(url_for("blog"))
        else:
            flash(_('Ошибка валидации!'))

    return render_template("create_post.html", form=form, tags=all_tags)

@application.route("/blog/<slug>")
def post_details(slug):
    page = request.args.get("page")
    page = int(page) if page and page.isdigit() else 1

    posts = Post.query.order_by(-Post.id)
    pages = posts.paginate(page=page, per_page=5)

    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    post_content = render_markdown(post.content)

    return render_template("post_details.html", post=post, post_content=post_content, pages=pages)

@application.route("/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first()

    if request.method == "POST":
        form = CreatePostForm(formdata=request.form, obj=post)
        form.populate_obj(post)
        post.slug = generate_slug(post.title)

        db.session.commit()
        flash(_('Пост изменен!'))
        return redirect(url_for("post_details", slug=post.slug))

    form = CreatePostForm(obj=post)
    return render_template("create_post.html", form=form)

@application.route("/user/<int:user_id>")
def user_details(user_id):
    page = request.args.get("page")
    page = int(page) if page and page.isdigit() else 1

    user = User.query.filter_by(id=user_id).first()
    if not user:
        abort(404)
    posts = user.posts
    pages = posts.paginate(page=page, per_page=2)

    return render_template("user_details.html", user=user, pages=pages)

@application.route("/tag/<slug>")
def tag_details(slug):
    tag = Tag.query.filter_by(slug=slug).first()
    if not tag:
        abort(404)

    page = request.args.get("page")
    page = int(page) if page and page.isdigit() else 1

    posts = tag.posts
    pages = posts.paginate(page=page, per_page=2)

    return render_template("tag_details.html", tag=tag, pages=pages)

@application.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    user = current_user
    form = RegForm(obj=user)

    if request.method == "POST":
        form = RegForm(formdata=request.form, obj=user)
        user.name = form.name.data
        user.last_name = form.last_name.data
        user.login = form.login.data
        if form.password.data:
            user.set_password(form.password.data)
        avatar_file = request.files.get("avatar")
        if avatar_file and avatar_file.filename:
            user.avatar = sqlite3.Binary(avatar_file.read())

        db.session.add(user)
        db.session.commit()
        flash(_('Данные изменены!'))

    page = request.args.get("page")
    page = int(page) if page and page.isdigit() else 1

    posts = user.posts
    pages = posts.paginate(page=page, per_page=5)
    return render_template("profile.html", user=user, pages=pages, form=form)

@application.route("/follow/<login>")
@login_required
def follow(login):
    user = User.query.filter_by(login=login).first()
    if not user:
        flash(_('Пользователь не найден :('))
        return redirect(url_for("index"))
    if current_user == user:
        flash(_('Вы не можете подписаться на самого себя!'))
        return redirect(url_for("user_details", user_id=user.id))
    current_user.follow(user)
    db.session.commit()
    flash(_('Подписка оформлена!'))
    return redirect(url_for("user_details", user_id=user.id))

@application.route("/unfollow/<login>")
@login_required
def unfollow(login):
    user = User.query.filter_by(login=login).first()
    if not user:
        flash(_('Пользователь не найден :('))
        return redirect(url_for("index"))
    if current_user == user:
        flash(_('Вы не можете отписаться от самого себя!'))
        return redirect(url_for("user_details", user_id=user.id))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('Вы успешно отписались от пользователя!'))
    return redirect(url_for("user_details", user_id=user.id))

@application.route("/user_avatar/<int:user_id>")
def user_avatar(user_id):
    user = User.query.get(user_id)
    if not user or not user.avatar:
        abort(404)
    h = make_response(user.avatar)
    h.headers["Content-Type"] = "image/png"
    return h

# Маршрут для установки языка
@application.route('/set_language/<lang>')
def set_language(lang=None):
    if lang not in application.config['BABEL_SUPPORTED_LOCALES']:
        lang = application.config['BABEL_DEFAULT_LOCALE']

    response = make_response(redirect(request.referrer or url_for('index')))
    response.set_cookie('lang', lang, max_age=30 * 24 * 60 * 60)  # Сохраняем язык в cookies на 30 дней
    return response

# установка темы приложения
@application.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    current_theme = request.cookies.get('theme')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    response = make_response(jsonify({'theme': new_theme}))
    response.set_cookie('theme', new_theme, max_age=30 * 24 * 60 * 60)  # Устанавливаем cookie с новой темой
    return response





