# from flask import Blueprint, render_template,request,flash
# from flask import redirect, url_for
# from flask_login import logout_user, login_required

# auth = Blueprint('auth', __name__)

# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     data = request.form
#     print(data)
#     return render_template("login.html")

# @auth.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         first_name = request.form.get('firstName')
#         password1 = request.form.get('password1')
#         password2 = request.form.get('password2')
#         print(email, first_name, password1, password2)
#         if len(email) < 4:
#             flash('Email must be greater than 3 characters.', category='error')
#         elif len(first_name) < 2:
#             flash('First name must be greater than 1 character.', category='error')
#         elif password1 != password2:
#             flash('Passwords don\'t match.', category='error')
        
#     return render_template("signup.html")


  


# @auth.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('auth.login'))

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # These names must match the "name" attributes in login.html.
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash('Logged in successfully.', category='success')
            return redirect(url_for('views.home'))

        flash('Incorrect email or password.', category='error')

    return render_template("login.html")


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # request.form.get() returns None when the field name doesn't exist,
        # and len(None) is what raised the TypeError. Defaulting to '' fixes it,
        # and the names below now match the ones in signup.html.
        email = (request.form.get('email') or '').strip()
        username = (request.form.get('username') or '').strip()
        password1 = request.form.get('password') or ''
        password2 = request.form.get('confirm_password') or ''

        if User.query.filter_by(email=email).first():
            flash('That email already has an account.', category='error')
        elif User.query.filter_by(username=username).first():
            flash('That username is taken.', category='error')
        elif len(email) < 4:
            flash('Email must be longer than 3 characters.', category='error')
        elif len(username) < 2:
            flash('Username must be longer than 1 character.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        else:
            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password1),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created.', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html")


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))