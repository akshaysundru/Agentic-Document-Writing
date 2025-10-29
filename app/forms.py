
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Regexp

class LoginForm(FlaskForm):
    """
    User login form with username/password authentication.

    Fields:
        username: Required username field
        password: Required password field  
        remember_me: Optional checkbox for persistent sessions
        submit: Form submission button
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class SignupForm(FlaskForm):
    """
    User registration form for creating new accounts.

    Fields:
        username: Required unique username
        password: Required password
        confirmpassword: Password confirmation (must match password)
        usertype: Role selection (Unit Coordinator or Admin)
        submit: Form submission button

    Validation:
        - Password and confirm password must match
        - All fields are required
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmpassword = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Sign Up')