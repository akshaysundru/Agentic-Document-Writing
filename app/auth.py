"""
Authentication module for user login, signup, and logout functionality.

Handles all authentication-related routes using Flask-Login for session management
and Werkzeug for secure password hashing.
Provides endpoints for user registration, login, and logout operations.
"""

from flask import render_template, redirect, url_for, request, flash, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from .forms import LoginForm, SignupForm
from .models import User
from . import db

# Create authentication blueprint for modular route organization
auth = Blueprint("auth", __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login page and authentication.

    GET: Display the login form
    POST: Process login credentials and authenticate user
    """
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query database for user
        userDB = User.query.filter_by(username=username).first()

        if userDB is None or not check_password_hash(userDB.password_hash, password): # pyright: ignore[reportArgumentType]
            flash("Login failed. Double-check your credentials.", 'error')
            return redirect("/login")
        else:
            # Successful login
            login_user(userDB, remember=form.remember_me.data)
            flash("Logged in successfully!", "success")
            return redirect(url_for('main.dashboard', username=userDB.username))

    return render_template('login.html', title='Sign In', form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user registration page and account creation.

    GET: Display the signup form
    POST: Process registration and create new user account
    """
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if username already exists
        userDB = User.query.filter_by(username=username).first()
        if userDB:
            flash("Username already in use.", 'error')
            return redirect('/signup_page')

        # Hash password
        hashedPassword = generate_password_hash(password) # type: ignore

        # Create new user
        newUser = User(
            username=username, # type: ignore
            password_hash=hashedPassword # type: ignore
        )

        # Save to database
        db.session.add(newUser)
        db.session.commit()

        flash("Account created successfully! You can now log in.", 'success')
        return redirect("/login")

    return render_template('signup.html', title='Sign Up', form=form)


@auth.route('/logout')
def logout():
    """
    Handle user logout and session termination.

    Clears the user session and redirects to home page.
    """
    logout_user()
    flash("Logged out.", "success")
    return redirect("/login")
