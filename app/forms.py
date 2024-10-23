from wtforms import Form, StringField, TextAreaField, FileField, PasswordField
from flask_babel import lazy_gettext as _l


class RegForm(Form):
    name = StringField(_l('Имя'))
    last_name = StringField(_l('Фамилия'))
    login = StringField(_l('Логин'))
    password = PasswordField(_l('Пароль'))
    avatar = FileField()

class LoginForm(Form):
    login = StringField(_l('Логин'))
    password = PasswordField(_l('Пароль'))


class CreatePostForm(Form):
    title = StringField(_l('Заголовок поста'))
    description = TextAreaField(_l('Описание поста (до 50 символов)'))
    content = TextAreaField(_l('Текст поста'))