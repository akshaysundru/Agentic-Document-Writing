from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/hello')
def index():
    return "Hello, World!"