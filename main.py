import os
import time
import random
import string
from datetime import datetime
from email_sender import send_email
from extensions import db, bcrypt, login_manager
from models import User, Task, Recovery
from forms import SignupForm, LoginForm, ForgotPassword, RecoveryCode, ResetPassword
from forms import  TaskForm, DeleteAll, MarkTask, DeleteTask
from flask_login import login_required, login_user, logout_user, current_user
from flask import Flask, render_template, url_for, redirect, flash

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"


def clean_recovery():
    all_recoveries = Recovery.query.all()
    for recovery in all_recoveries:
        time_elapsed = time.time() - recovery.sent_at
        if time_elapsed >= (10 * 60):
            db.session.delete(recovery)
    db.session.commit()


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    task_form = TaskForm()
    delete_all = DeleteAll()
    mark_task = MarkTask()
    delete_task = DeleteTask()
    date = datetime.now().strftime("%A %B %d, %Y")

    if task_form.add.data:
        if task_form.validate():
            new_task = Task(user_id=current_user.id, title=task_form.task.data)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for("home"))

    elif delete_all.delete_all.data:
        if delete_all.validate():
            all_tasks = Task.query.filter_by(user_id=current_user.id).all()
            for task in all_tasks:
                db.session.delete(task)
            db.session.commit()
            return redirect(url_for("home"))

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks, form=task_form, date=date,
                            delete_all=delete_all, mark_task=mark_task, delete_task=delete_task)


@app.route("/mark_task/<int:task_id>", methods=["POST"])
@login_required
def mark_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        task.completed = True
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user = User.query.filter_by(username=username).first()
        if user is not None and bcrypt.check_password_hash(user.password, password):
            user.last_login = datetime.now()
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")

    return render_template("login.html", form=login_form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    signup_form = SignupForm()
    if signup_form.validate_on_submit():
        user_name = User.query.filter_by(username=signup_form.username.data).first()
        user_email = User.query.filter_by(email=signup_form.email.data).first()

        if user_email:
            flash("This email has already signed up.")        
        elif user_name:
            flash("This username is already taken.")
        else:
            hashed_password = bcrypt.generate_password_hash(signup_form.password.data).decode('utf-8')
            new_user = User(username=signup_form.username.data,
                            email=signup_form.email.data,
                            password=hashed_password,
                            joined_at=datetime.now(),
                            last_login=datetime.now())
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
        
    return render_template("register.html", form=signup_form)


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    forgot_form = ForgotPassword()
    if forgot_form.validate_on_submit():
        clean_recovery()
        email = forgot_form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            recovery_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            sent = send_email(user.email, recovery_code)
            if sent:
                recovery = Recovery(user_id=user.id,
                                    code=recovery_code,
                                    sent_at=time.time())
                db.session.add(recovery)
                db.session.commit()
                return redirect(url_for("verify_code", email=email))
            else:
                flash("Could not send the email. Please try again later.")
        else:
            flash("Email does not exist.")

    return render_template("forget_password.html", form=forgot_form)


@app.route("/verify_code/<email>", methods=["GET", "POST"])
def verify_code(email):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    code_form = RecoveryCode()
    if code_form.validate_on_submit():
        clean_recovery()
        user = User.query.filter_by(email=email).first()
        if not user:
            return redirect(url_for("forgot_password"))
        
        recovery = Recovery.query.filter_by(user_id=user.id).all()
        if not recovery:
            flash("Your code has been expired.")
            return redirect(url_for("forgot_password"))
        if recovery[-1].code == code_form.code.data:
            login_user(user)
            return redirect(url_for("reset_password"))
        
        flash("Code is incorrect. Try again.")
        return redirect(url_for("verify_code", email=email))
    
    return render_template("verify_code.html", form=code_form, email=email)


@app.route("/reset_password", methods=["GET", "POST"])
@login_required
def reset_password():
    reset_form = ResetPassword()
    if reset_form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, reset_form.password.data):
            flash("You can not choose your previous password.")
        else:
            hashed_password = bcrypt.generate_password_hash(reset_form.password.data).decode('utf-8')
            current_user.password = hashed_password
            Recovery.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            return redirect(url_for("home"))

    return render_template("reset_password.html", form=reset_form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
