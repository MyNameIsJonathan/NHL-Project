from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flasksite import db, bcrypt
from flasksite.models import User
from flasksite.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flasksite.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user) #Create user instance
        db.session.commit() #Commit user to the database
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() #Returns None
                                                           # if no user is found
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data): #If user is
                                               # found and the passwords match
            login_user(user, remember=form.remember.data) #If the user checked
            # the Remember Me box, that information is stored in form.remember
            next_page = request.args.get('next') #This allows us to redirect to
            # the intended page after being forced to login
            #request.args is a dictionary, so using the method .get() returns
            # the key if it is present but returns None if not. This means no
            # KeyError is raised if the key (next) is not in the dictionary
            return  redirect(next_page) if next_page else redirect(
                url_for('main.home')) #Ternary conditional
        else:
            flash('Incorrect Login. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit(): #Edit the entries into the db for the email
                                  # and usernames submitted to be changed
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET': #Autofill entry cells with current username and email
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An instructional email has been sent to reset your password.',
              'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password',
                           form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    else:
        form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit() #Commit user to the database
        flash('Your password has been updated!', 'success')
        return redirect(url_for('users.login'))
