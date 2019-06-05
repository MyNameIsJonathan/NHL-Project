import time

import recurly

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flasksite import db, bcrypt
from flasksite.models import User
from flasksite.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm)
from flasksite.users.utils import save_picture
from flasksite.config import Config
import flaskAccessories as fa

# Establish recurly information
myConfig = Config()
recurly.SUBDOMAIN = myConfig.RECURLY_SUBDOMAIN
recurly.API_KEY = myConfig.RECURLY_API_KEY
recurly.DEFAULT_CURRENCY = 'USD'


# Instantiate the blueprint
users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
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
            # request.args is a dictionary, so using the method .get() returns
            # the key if it is present but returns None if not. This means no
            # KeyError is raised if the key (next) is not in the dictionary
            return  redirect(next_page) if next_page else redirect(
                url_for('main.home')) #Ternary conditional
        else:
            flash('Incorrect Login. Please check email and password', 'danger')

    return render_template('login.html',
                           title='Login',
                           form=form)

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

    # Get currnet_user's recurly account to pass to account.html.
    # Will differentiate between users with subscriptions and those without
    current_user_account_code = fa.create_account_code(current_user.id)
    user_recurly_account = recurly.Account.get(current_user_account_code)

    # Create a list that will be used for dynamic display in /account
    if user_recurly_account.has_active_subscription:
        is_subscribed = ['Yes']
    else:
        is_subscribed = []


    return render_template('account.html', title='Account',
                           image_file=image_file, form=form,
                           is_subscribed=is_subscribed)



@users.route("/create_recurly_account")
def create_recurly_account():
    return render_template('create_recurly_account.html')

@users.route("/subscribe", methods=['GET', 'POST'])
def subscribe():

    # If user is not logged in, have them login or register
    if not current_user.is_authenticated:
        flash('Please login or register to create an account first!', 'danger')
        time.sleep(1)
        return redirect(url_for('users.login'))

    return render_template('subscribe.html', title='Subscribe')

@users.route("/update_recurly_account")
def update_recurly_account():

    # If user is not logged in, have them login or register
    if not current_user.is_authenticated:
        flash('Please login or register to create an account first!', 'danger')
        return redirect(url_for('users.login'))



    try:

        # Load user account
        user_account_code = fa.create_account_code(current_user.id)
        user_account = recurly.Account.get(user_account_code)

        new_account = recurly.Account(
            account_code=user_account_code,
            billing_info=recurly.BillingInfo(
                token_id=request.form['recurly-token']
                )
            )

        flash('Account subscribed successfully!', 'success')
        return redirect(url_for('users.account'))


    except recurly.ValidationError:
        flash('ValidationError! Please try again shortly.', 'danger')
        return redirect(url_for('users.account'))


# POST route to handle a new account form
# From: https://github.com/recurly/recurly-js-examples/blob/master/api/python/app.py#L50-62
@users.route("/api/accounts/new", methods=['POST'])
def new_recurly_account():

    # If user is not logged in, have them login or register
    if not current_user.is_authenticated:
        flash('Please login or register to create an account first!', 'danger')
        return redirect(url_for('users.login'))

    # Create user's account_code from hidden hash library
    user_account_code = fa.create_account_code(current_user.id)

    try:

        # Create user account
        new_account = recurly.Account(
            account_code=user_account_code,
            billing_info=recurly.BillingInfo(
                token_id=request.form['recurly-token']
                )
            )

        # Create subscription
        subscription = recurly.Subscription()
        subscription.plan_code = request.form['plan']
        subscription.currency = 'USD'
        subscription.account = new_account
        subscription.save()

        flash('Account subscribed successfully!', 'success')
        return redirect(url_for('users.account'))

    except recurly.ValidationError:
        flash('ValidationError! Please try again shortly.', 'danger')
        return redirect(url_for('users.account'))

# POST route to handle a new subscription form
@users.route("/api/subscriptions/new", methods=['POST'])
def new_subscription():

    # If user is not logged in, have them login or register
    if not current_user.is_authenticated:
        flash('Please login or register to create an account first!', 'danger')
        return redirect(url_for('users.login'))

    # We'll wrap this in a try to catch any API
    # errors that may occur
    try:

        # Get the user_account
        user_account_code = fa.create_account_code(current_user.id)
        user_account = recurly.Account.get(user_account_code)
        billing_info = recurly.BillingInfo(
            token_id=request.form['recurly-token'])
        user_account.billing_info = billing_info

        # Create the scubscription using minimal
        # information: plan_code, account_code, currency and
        # the token we generated on the frontend
        subscription = recurly.Subscription(
            currency='USD',
            account=user_account,
            plan_code='testplancode')

    except:
        flash(('Sorry, our servers experienced an issue creating your'
               'subscription. Please try again later!'), 'danger')
    # The subscription has been created and we can redirect to a confirmation page
    subscription.save()
    flash('You have been successfully subscribed to the Basic Plan!', 'success')
    return redirect(url_for('main.home'))
