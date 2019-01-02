
import os
import secrets
from PIL import Image, ImageOps
from flask import url_for, current_app
from flask_mail import Message
from flasksite import mail

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    #Reshape image to maximum possible square and resize to reduce image size
    i = Image.open(form_picture)
    width, height = i.size
    new_width, new_height = min(width, height), min(width, height)

    left = (width - new_width)/2
    top = (height - new_height)/2
    right = (width + new_width)/2
    bottom = (height + new_height)/2

    i = i.crop((left, top, right, bottom))
    i.thumbnail((125, 125), Image.ANTIALIAS)
    i.save(picture_path)
    
    return picture_fn


def send_reset_email(user): #NOT CURRENTLY FUNCTIONAL
    """Sends reset email from personal account to users account, with link to reset password"""
    token = user.get_reset_token()
    msg = Message('Password Reser Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, then simply ignore this email and no changes will be made.
'''
    mail.send(msg)