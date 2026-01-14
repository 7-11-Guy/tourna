import os
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# --- SQLITE CONFIG (PRODUCTION SAFE) ---
basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(basedir, "app.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- MODEL ---
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    birthday = db.Column(db.Date, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- ROUTES ---
@app.route("/")
def home():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    birthday_str = request.form.get("birthday")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if not all([birthday_str, first_name, last_name, email, password, confirm_password]):
        flash("All fields are required", "error")
        return redirect(url_for("home"))

    if password != confirm_password:
        flash("Passwords do not match", "error")
        return redirect(url_for("home"))

    try:
        birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid birthday format", "error")
        return redirect(url_for("home"))

    if User.query.filter_by(email=email).first():
        flash("Email already exists", "error")
        return redirect(url_for("home"))

    new_user = User(
        birthday=birthday,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=generate_password_hash(password),
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("success"))
    except Exception as e:
        db.session.rollback()
        flash("Database error", "error")
        print(e)
        return redirect(url_for("home"))

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/users")
def users():
    return render_template("users.html", users=User.query.all())

# --- RUN ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

        db.create_all()
    app.run(debug=True)
