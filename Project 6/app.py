import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True, cascade="all, delete")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    @app.route("/")
    def index():
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template("index.html", posts=posts)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if len(username) < 3:
                flash("Username must be at least 3 characters.", "danger")
            elif len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
            elif User.query.filter_by(username=username).first() is not None:
                flash("Username already exists.", "danger")
            else:
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash("Logged in successfully.", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid username or password.", "danger")

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
        return render_template("dashboard.html", posts=posts)

    @app.route("/post/new", methods=["GET", "POST"])
    @login_required
    def create_post():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()

            if not title or not content:
                flash("Title and content are required.", "danger")
            else:
                post = Post(title=title, content=content, user_id=current_user.id)
                db.session.add(post)
                db.session.commit()
                flash("Post created successfully.", "success")
                return redirect(url_for("dashboard"))

        return render_template("post_form.html", page_title="Create Post", post=None)

    @app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_post(post_id: int):
        post = Post.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            flash("You can only edit your own posts.", "danger")
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()

            if not title or not content:
                flash("Title and content are required.", "danger")
            else:
                post.title = title
                post.content = content
                db.session.commit()
                flash("Post updated successfully.", "success")
                return redirect(url_for("dashboard"))

        return render_template("post_form.html", page_title="Edit Post", post=post)

    @app.route("/post/<int:post_id>/delete", methods=["POST"])
    @login_required
    def delete_post(post_id: int):
        post = Post.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            flash("You can only delete your own posts.", "danger")
            return redirect(url_for("dashboard"))

        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.", "info")
        return redirect(url_for("dashboard"))

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
