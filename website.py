# qi: smart notes
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from forms import SettingsForm, SigninForm, SignupForm
import math
import logging
import argparse
import json

from datetime import datetime

import settings
import db_api
import utils
from models import User, Entry

app = Flask(__name__)

db = db_api.QiDB()

@app.before_request
def before_request():
    g.user = session.get('user')
    g.numpages = int(math.ceil(float(g.user.entry_count()) / float(settings.ITEMS_PER_PAGE)))

@app.route("/")
@app.route("/page/<int:pagenum>")
def page(pagenum=0):
    """Display a specific page"""
    today_id = datetime.now().strftime('%Y%m%d')
    if g.user:
        entries = g.user.entries(page=pagenum)
    else:
        entries = None
    return render_template("index.html",
                           entries=entries)



@app.route("/save", methods=['POST'])
def save_entry():
    """Save the entry (ajax)"""
    user = session['user']
    entry_id = request.form['entry_id']
    raw_body = request.form['raw_body']

    assert user
    assert entry_id
    assert isinstance(entry_id, basestring)
    assert isinstance(raw_body, basestring)

    entry = Entry(entry_id, user.username)
    entry.raw_body = raw_body

    entry = entry.save()
    return json.dumps(entry.to_json())


@app.route("/delete", methods=['POST', 'DELETE'])
def delete_entry():
    """Delete the entry"""
    user = session['user']
    entry_id = request.form['entry_id']

    assert user
    assert entry_id
    assert isinstance(entry_id, basestring)

    entry = Entry(entry_id, user.username)
    assert entry.created_by == user.username

    entry = entry.delete()
    return "ok"


@app.route("/topic/<topic>")
def show_topic(topic):
    """Show the topic page"""
    entries = list(db.get_tagged_entries(g.user.username, topic))
    return render_template("index.html",
                           topic=topic,
                           entries=entries)


@app.route("/search", methods=['POST'])
def search_redirect():
    term = request.form['searchterm']
    return redirect(url_for('search', term=term))


@app.route("/search/<term>", methods=['GET', 'POST'])
def search(term):
    """Search for <term>"""
    results = list(db.search_user_entries(g.user.username, term))
    return render_template("index.html",
                           searchterm=term,
                           entries=results)


@app.route("/newentry", methods=['GET','POST'])
def newentry():
    """Create a new entry"""
    user = session['user']
    assert user

    new_entry = Entry(None, user.username)
    new_entry.save()

    logging.info("Creating a new entry with id {} for user {}".format(new_entry.id, user.username))
    if request.method == 'GET':
        return redirect(url_for('home'))
    else:
        return new_entry


@app.route("/settings", methods=['GET', 'POST'])
def user_settings():
    """User settings"""
    user = session['user']
    form = SettingsForm(email=user.email)

    if request.method == 'POST' and form.validate():
        user_changed = False
        if request.form['email'] and request.form['email'] != user.email:
            user.email = request.form['email']
            user_changed = True
            flash("Email address saved!")
        if request.form['password']:
            user.set_password(request.form['password'])
            user_changed = True
            user.save()
            flash("Your password was successfully changed!")

        if user_changed:
            user.save()

        return redirect(url_for('home'))

    return render_template("settings.html",
                           form=form)


@app.route("/topics")
def topics():
    """A list of the user's topics"""
    return render_template("topics.html")


@app.route("/signin", methods=['GET', 'POST'])
def sign_in():
    """Sign the user in"""
    form = SigninForm()
    user = None
    if request.method == 'POST' and form.validate():
        # Log the user in
        username = request.form['username']
        password = request.form['password']

        assert isinstance(username, basestring)
        assert isinstance(password, basestring)

        user = User(username)
        if user.authenticate(password):
            session['user'] = user
            logging.info("User signed in: {}".format(username))
            return redirect(url_for('home'))
        else:
            flash("Incorrect username or password")
            logging.info("Incorrect username or password for user: {}".format(username))
            return render_template("signin.html", form=form, user=user)
    return render_template("signin.html",
                           form=form,
                           user=user)


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    """Register a user"""
    form = SignupForm()
    user = None

    if request.method == 'POST' and form.validate():
        # Add the user
        username = request.form['username']
        password = request.form['password']

        if username and password:
            if db.get_user(username):
                # This username already exists
                flash("This username has already been reserved, please choose another")
                return render_template("signup.html",
                                       form=form,
                                       user=None)

            user = User(username)
            user.set_password(password)

            user.save()
            # Log the user in
            session['user'] = user

            # Create a new entry for the user so they have something to look at
            new_entry = Entry(None, user.username)
            new_entry.raw_body = """Double-click in this area or use the edit button to edit this entry!

Create tags by adding a "#" before a word, like this: #mytag
"""
            new_entry.save()

            logging.info("User created: {}".format(username))

            flash("Successfully registered. Welcome, {}!".format(username))
            return redirect(url_for('home'))
    return render_template("signup.html",
                           form=form,
                           user=user)


@app.route("/signout")
def sign_out():
    session.pop('user')
    return redirect(url_for('home'))


# Admin functionality
@app.route("/admin")
def admin():
    """Administration homepage"""
    users = db.get_user_list()
    return render_template("admin.html",
                           users=users)

@app.route("/admin/edituser/<username>")
def admin_edit_user(username):
    """Administrative screen to edit a user"""
    admin_user = session['user']
    if not admin_user.is_admin():
        logging.info("Invalid admin access attempt from {}".format(admin_user.username))
        return redirect(url_for('home'))

    edit_user = User(username)
    assert edit_user

    return render_template("adminedituser.html",
                           edit_user=edit_user)

@app.route("/setpass")
@app.route("/setpass/<token>", methods=['GET', 'POST'])
def gen_reset_token(token=None):
    """Generate a user reset token for <username>"""
    print "token: ", token
    return "ok"

@app.route("/resetpw/<token>", methods=['GET', 'POST'])
def reset_pw(token):
    """Look up a user with <token>, and allow the user to reset the password.
    This is a one-time operation. <token> should expire after the page is viewed.
    If the user tries to reload or view the page later, they'll have to request
    another reset."""

    return "pok"


def init_logging(args):
    log_level = logging.INFO
    log_format = '%(asctime)s %(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format)

    handlers = []

    # Console handler.  By default, the console receives all log
    # messages.  If the user is logging to a file, then the console
    # will only receive warnings and errors.
    console = logging.StreamHandler()
    console.setLevel(logging.WARN if getattr(args, 'logfile', False) else log_level)
    console.setFormatter(formatter)
    handlers.append(console)

    # File handler.  Optional.  If used, the file will receive all log
    # messages.
    if getattr(args, 'logfile', False):
        filehandler = logging.FileHandler(args.logfile, 'a')
        filehandler.setFormatter(formatter)
        filehandler.setLevel(log_level)
        handlers.append(filehandler)

    # Attach all active log handlers.
    logger = logging.getLogger()
    logger.setLevel(log_level)
    for old_handler in logger.handlers:
        logger.removeHandler(old_handler)
    for new_handler in handlers:
        logger.addHandler(new_handler)


app.secret_key = settings.APP_SECRET_KEY

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', metavar='FILE', help='Send all log messages to a file. ' +
                                                          'Console will only display warnings & errors.')
    parser.add_argument('--debug', action='store_true', default=False, help='Turn on debug log messages.')
    args = parser.parse_args()

    init_logging(args)
    app.run(port=settings.APP_PORT,
            debug=settings.APP_DEBUG_ENABLED,
            use_reloader=settings.APP_RELOADER_ENABLED)
