# from flask import Blueprint,render_template

# views = Blueprint('views', __name__)
# @views.route('/')
# @views.route('/home')
# def home():
#     return render_template("home.html")

# @views.route('/signup')
# def signup():
#     return render_template("signup.html")

# @views.route('/login')
# def login():
#     return render_template("login.html", text = "Login Page")


import json

from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

from . import db
from .models import Note

views = Blueprint('views', __name__)


# NOTE: the /login and /signup routes that used to live here have been removed.
# They collided with the ones in auth.py, which is why POSTing the forms
# behaved strangely.
@views.route('/', methods=['GET', 'POST'])
@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = (request.form.get('note') or '').strip()

        if len(note) < 1:
            flash('Note is too short.', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added.', category='success')

    return render_template("home.html")


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    # index.js sends the note id as a JSON body.
    payload = json.loads(request.data)
    note = db.session.get(Note, payload.get('noteId'))

    if note is not None and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()

    return jsonify({})
