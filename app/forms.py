from wtforms import Form, StringField, TextAreaField, FileField


class RegForm(Form):
    name = StringField("Имя")
    last_name = StringField("Фамилия")
    login = StringField("Логин")
    password = StringField("Пароль")
    avatar = FileField()

class LoginForm(Form):
    login = StringField("Логин")
    password = StringField("Пароль")


class CreatePostForm(Form):
    title = StringField("Заголовок поста")
    description = TextAreaField("Описание поста (до 50 символов)")
    content = TextAreaField("Текст поста")