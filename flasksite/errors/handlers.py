from flask import Blueprint, render_template, url_for, flash

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

@errors.app_errorhandler(500)
def error_500(error):
    flash('Sorry, we are currently experiencing some difficulties!')
    return render_template(url_for('main.home'))

