from flask import render_template, request, redirect, url_for, flash, abort, make_response
from flask_login import login_user, logout_user, login_required, current_user
import sqlite3
import markdown

from app import application
from app.forms import *
from app.models import *

@application.route("/")
def index():
    return render_template("index.html")

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
        avatar = request.files.get("avatar").read()

        user = User(name=name, last_name=last_name, login=login, password=password, avatar=sqlite3.Binary(avatar))
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
        if user and user.password == user_password:
            login_user(user)
            flash("Вы успешно авторизовались!")
            return redirect(next) if next else redirect("blog")
        else:
            flash("Неверный логин или пароль!")
            return redirect(url_for("login"))

    form = LoginForm()
    return render_template("login.html", form=form)

@application.route("/logout")
def logout():
    logout_user()
    flash("Вы вышли из аккаунта!")
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
    s = request.args.get('s')

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
            flash("Пост создан!")
            return redirect(url_for("blog"))
        else:
            flash("Ошибка валидации!")

    return render_template("create_post.html", form=form, tags=all_tags)

@application.route("/<slug>")
def post_details(slug):
    page = request.args.get("page")
    page = int(page) if page and page.isdigit() else 1

    posts = Post.query.order_by(-Post.id)
    pages = posts.paginate(page=page, per_page=5)

    post = Post.query.filter_by(slug=slug).first()
    # Конвертируем Markdown в HTML
    post_content = markdown.markdown(post.content, extensions=['fenced_code', 'codehilite', 'tables'])

    return render_template("post_details.html", post=post, post_content=post_content, pages=pages)

@application.route("/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first()

    if request.method == "POST":
        form = CreatePostForm(formdata=request.form, obj=post)
        form.populate_obj(post)

        db.session.commit()
        flash("Пост изменен!")
        return redirect(url_for("post_details", slug=post.slug))

    form = CreatePostForm(obj=post)
    return render_template("create_post.html", form=form)

@application.route("/user/<int:user_id>")
def user_details(user_id):
    page = request.args.get("page")
    page = int(page) if page and page.isdigit() else 1

    user = User.query.filter_by(id=user_id).first()
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
        user.password = form.password.data
        user.avatar = sqlite3.Binary(request.files.get("avatar").read()) if request.files.get("avatar") else user.avatar

        db.session.add(user)
        db.session.commit()
        flash("Данные изменены")

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
        flash("Пользователь не найден :(")
        return redirect(url_for("index"))
    if current_user == user:
        flash("Вы не можете подписаться на самого себя!")
        return redirect(url_for("user_details", user_id=user.id))
    current_user.follow(user)
    db.session.commit()
    flash("Подписка оформлена!")
    return redirect(url_for("user_details", user_id=user.id))

@application.route("/unfollow/<login>")
@login_required
def unfollow(login):
    user = User.query.filter_by(login=login).first()
    if not user:
        flash("Пользователь не найден :(")
        return redirect(url_for("index"))
    if current_user == user:
        flash("Вы не можете отписаться от самого себя!")
        return redirect(url_for("user_details", user_id=user.id))
    current_user.unfollow(user)
    db.session.commit()
    flash("Вы успешно отписались!")
    return redirect(url_for("user_details", user_id=user.id))

@application.route("/user_avatar/<int:user_id>")
def user_avatar(user_id):
    user = User.query.get(user_id)
    if user.avatar:
        user_avatar = user.avatar
        h = make_response(user_avatar)
        h.headers["Content-Type"] = "image/png"
    else:
        h = ""
    return h