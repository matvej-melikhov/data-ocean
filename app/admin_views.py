from flask import url_for, redirect, request
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from app.models import *


class AdminMixin():
    def is_accessible(self):
        try:
            is_admin = current_user.is_admin()
        except AttributeError:
            is_admin = False
        return is_admin

    def inaccessible_callback(self, *args):
        return redirect(url_for("login", next=request.url))

class MyAdminIndexView(AdminMixin, AdminIndexView):
    pass


class MyModelView(AdminMixin, ModelView):
    column_display_pk = True


class PostView(MyModelView):
    column_list = ["id", "title", "content", "slug", "tags", "author"]
    form_columns = ["title", "content", "slug", "tags", "author"]

class UserView(MyModelView):
    column_list = ["id", "name", "last_name", "login", "password", "roles", "followers", "followed"]
    form_columns = ["id", "name", "last_name", "login", "password", "roles", "followers", "followed"]


from app import application, admin

admin.template_mode = "bootstrap3"
admin.init_app(application, index_view=MyAdminIndexView(name="Home"))

admin.add_view(PostView(Post, db.session))
admin.add_view(MyModelView(Tag, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(MyModelView(Role, db.session))