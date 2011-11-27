# qi: smart notes
from flask import Flask, render_template, request, redirect, url_for, session, flash
from forms import SigninForm, SignupForm
import logging
import argparse

import bcrypt
from datetime import datetime

import settings
import db_api
import utils
from models import User, Entry

app = Flask(__name__)

db = db_api.QiDB()

@app.route("/")
def home():
    """Display the home page"""
    today_id = datetime.now().strftime('%Y%m%d')
    user = session.get('user')
    if user:
        entries = user.entries()
        current_entry = user.current_entry()
        scratchpad = user.scratchpad()
    else:
        entries = []
        scratchpad = None
        current_entry = None

    return render_template("index.html",
                           scratchpad=scratchpad,
                           user=user,
                           entries=entries,
                           current_entry=current_entry,
                           current_date=datetime.now())


@app.route("/save", methods=['POST'])
def saveentry():
    """Save the entry (ajax)"""
    user = session['user']
    entry_id = request.form['entry_id']

    entry_record = db.get_entry(entry_id, user.username)
    created_at = None
    tags = []
    if entry_record:
        created_at = entry_record['created_at']
        tags = entry_record['tags']

    raw_body = request.form['raw_body']
    entry = Entry(raw_body, user.username, entry_id, tags, created_at)
    entry.save()
    logging.info("Saving entry with id {} for user {}".format(entry_id, user.username))
    return "ok"


@app.route("/newentry", methods=['GET','POST'])
def newentry():
    """Create a new entry"""
    user = session['user']

    current_entry = user.current_entry()
    if current_entry:
        newentry = Entry('', user.username, id=utils.nextid(current_entry.id))
    else:
        newentry = Entry('', user.username)
 
    db.save_entry(newentry)
    logging.info("Creating a new entry with id {} for user {}".format(newentry.id, user.username))
    if request.method == 'GET':
        return redirect(url_for('home'))
    else:
        return newentry


@app.route("/signin", methods=['GET', 'POST'])
def signin():
    """Sign the user in"""
    form = SigninForm()
    user = None
    if request.method == 'POST' and form.validate():
        # Log the user in
        username = request.form['username']
        password = request.form['password']
        user_record = db.get_user(username)
        if user_record and bcrypt.hashpw(password, user_record['password']):
            user = User(username, email=user_record['email'])
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
def signup():
    """Register a user"""
    form = SignupForm()
    user = session.get('user')
    if request.method == 'POST' and form.validate():
        # Add the user
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'], 
                                 bcrypt.gensalt(settings.BCRYPT_WORK_FACTOR))
        invitation_code = request.form['invitation_code']
        user = User(username, password)

        db.save_user(user)

        # Log the user in
        user = User(username, email='')
        session['user'] = user

        logging.info("User created: {}".format(username))

        flash("Successfully registered. Welcome, {}!".format(username))
        return redirect(url_for('home'))
    return render_template("signup.html",
                           form=form,
                           user=user)


@app.route("/signout")
def signout():
    session.pop('user')
    return redirect(url_for('home'))


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
