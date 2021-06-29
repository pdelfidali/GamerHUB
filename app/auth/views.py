import sqlalchemy.exc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email
from wtforms.fields.html5 import EmailField
from flask import Blueprint, render_template, redirect, url_for, flash
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from . import auth
from flask_login import login_user, logout_user, login_required


class RegisterForm(FlaskForm):
    username = StringField('Wprowadź swój username:', validators=[DataRequired(message='Pole nie może być puste')])
    email = EmailField('Wprowadź swój adres e-mail:', validators=[DataRequired(message='Pole nie może być puste'), Email(message='Wprowadź poprawny adres email')])
    password = PasswordField('Wprowadź hasło:', validators=[DataRequired(message='Pole nie może być puste')])
    password2 = PasswordField('Potwierdź hasło:', validators=[DataRequired(message='Pole nie może być puste')])
    submit = SubmitField('Zatwierdź')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    password_hash=generate_password_hash(form.password.data))
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Poprawnie zarejestrowano użytkownika {form.username.data}')
            return redirect('/')
        except sqlalchemy.exc.IntegrityError:
            flash(f'Błędny adres email lub nick')
    return render_template('auth.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    class LoginForm(FlaskForm):
        username = StringField('Wprowadź swój nick:', validators=[DataRequired(message='Pole nie może być puste')])
        password = PasswordField('Wprowadź hasło:', validators=[DataRequired(message='Pole nie może być puste')])
        remember_me = BooleanField('Nie wylogowywuj mnie')
        submit = SubmitField('Zaloguj się')

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect('/')
        flash('Niepoprawny nick lub hasło')
    return render_template('auth.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowałeś się!')
    return redirect('/')
