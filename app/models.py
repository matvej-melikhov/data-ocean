from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


def generate_slug(title):
    slug = title
    for i in [",", ".", "!", "?", ";", ":"]:
        slug = slug.replace(i, "-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

users_roles = db.Table("users_roles",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))
)

followers_followed = db.Table("followers_followed",
    db.Column("follower_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer(), db.ForeignKey("user.id"))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    login = db.Column(db.String(20), unique=True)
    password = db.Column(db.String())
    avatar = db.Column(db.LargeBinary)

    roles = db.relationship("Role", secondary=users_roles, backref=db.backref("users", lazy="dynamic"))
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    followed = db.relationship("User",
       secondary=followers_followed,
       primaryjoin=(followers_followed.c.follower_id == id),
       secondaryjoin=(followers_followed.c.followed_id == id),
       backref=db.backref("followers")
    )

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def is_admin(self):
        roles_names = [role.name.lower() for role in self.roles]
        return "админ" in roles_names or 'создатель' in roles_names

    def is_following(self, user):
        return user in list(self.followed)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def __repr__(self):
        return f"{self.name} {self.last_name}"


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    description = db.Column(db.String())

    def __repr__(self):
        return f"{self.name}"


posts_tags = db.Table("posts_tags",
    db.Column("post_id", db.Integer(), db.ForeignKey("post.id")),
    db.Column("tag_id", db.Integer(), db.ForeignKey("tag.id"))
)


class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.Text())
    content = db.Column(db.Text())
    slug = db.Column(db.String(), unique=True)

    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    tags = db.relationship("Tag", secondary=posts_tags, backref=db.backref("posts", lazy="dynamic"))

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.slug = generate_slug(self.title)
        self.author = current_user

    def __repr__(self):
        return f"{self.title}"


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True)
    slug = db.Column(db.String(), unique=True)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = generate_slug(self.name)

    def __repr__(self):
        return f"{self.name}"