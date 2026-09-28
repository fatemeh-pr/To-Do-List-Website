from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo


class SignupForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=5, max=250, message="Username must be 5-250 characters.")])
    email = EmailField("Email", validators=[InputRequired(), Email(), Length(max=250)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=10, max=50, message="Password must be 10-50 characters.")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired(), Length(min=10, max=50, message="Password must be 10-50 characters."), 
                                                            EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class TaskForm(FlaskForm):
    task = StringField("New Task", validators=[InputRequired(), Length(max=250)])
    add = SubmitField("Add")


class DeleteAll(FlaskForm):
    delete_all = SubmitField("Delete All Tasks")


class MarkTask(FlaskForm):
    done = SubmitField("Done")


class DeleteTask(FlaskForm):
    delete = SubmitField("Delete")


class ForgotPassword(FlaskForm):
    email = EmailField("Enter your email", validators=[InputRequired(), Email(), Length(max=250)])
    send = SubmitField("Send Code")


class RecoveryCode(FlaskForm):
    code = StringField("Enter the code:", validators=[InputRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verify")


class ResetPassword(FlaskForm):
    password = PasswordField("New Password", validators=[InputRequired(), Length(min=10, max=50, message="Password must be 10-50 characters.")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired(), Length(min=10, max=50, message="Password must be 10-50 characters."),
                                                            EqualTo("password", message="Passwords must match.")])
    reset = SubmitField("Reset Password")
